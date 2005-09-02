"""These are composite widgets, that is, widgets composed of more than one
XUL element, with special methods, and custom JS."""

from nufox import xul
from nevow import livepage
from twisted.internet.defer import Deferred

class Player(xul.GenericWidget):
    """I am a media player, I require either the helix or realplayer plugin"""

    def __init__(self, mediaURL, width=300, height=300):
        xul.GenericWidget.__init__(self)
        newKwargs = {
            'src' : mediaURL,
            'width' : width,
            'height' : height,
            'console' : 'one',
            'controls' : 'ImageWindow',
            'maintainaspect' : 'true' }
        self.kwargs = newKwargs

    def play(self):
        self.pageCtx.client.send(livepage.js.PlayerPlay(str(self.id)))

    def pause(self):
        self.pageCtx.client.send(livepage.js.PlayerPause(str(self.id)))

    def stop(self):
        self.pageCtx.client.send(livepage.js.PlayerStop(str(self.id)))

    def getTag(self):
        return xul.htmlns.embed(**self.kwargs)

class SequenceSubject(object):
    """
    I fill the role of a subject in the observer pattern.
    http://sern.ucalgary.ca/courses/SENG/609.04/W98/lamsh/observerLib.html
    I specialise at sequences which allows me to be
    a bit smarter in how I notify my observers of
    updates.
    """
    def __init__(self, seq=[]):
        self.data = seq
        self.observers = []

    def addObserver(self, ob, mapper):
        self.observers.append((ob, mapper))
        ob.notifySet([(item, mapper(item)) for item in self.data])

    def set(self, seq):
        self.data = seq
        for ob, mapper in self.observers:
            ob.notifySet([(item, mapper(item)) for item in self.data])

    def append(self, *items):
        self.data += items
        for ob, mapper in self.observers:
            ob.notifyAppend([(item, mapper(item)) for item in items])

    def remove(self, *items):
        for item in items:
            self.data.remove(item)
        for ob, mapper in self.observers:
            ob.notifyRemove(items)


class CompositeTreeBase(xul.GenericWidget):
    def __getattr__(self, name):
        """
        delegate most of genericwidget's interface to our tree widget
        """
        if name in [
            'children', 'id', 'pageCtx', 'rend', 'rendPostLive',
            'addHandler', 'handlers', 'getTag'
        ]:
            return getattr(self.tree, name)
        raise AttributeError, name


class SimpleTree(CompositeTreeBase):
    """
    I'm a simple tree widget for a 1 tier list of items

    @param headerLabels: a tuple of strings for the tree's
    column headers.

    @param kwargs: kwargs to configure the actual xul.Tree widget
    """

    def __init__(self, headerLabels, **kwargs):
        t = xul.Tree(**kwargs)
        th = xul.TreeCols()
        for cell in headerLabels:
            th.append(xul.TreeCol(flex=1, label=cell))
            th.append(xul.Splitter(_class="tree-splitter"))
        t.append(th)
        tc = xul.TreeChildren()
        t.append(tc)
        self.tree = t
        self.treeChildren = tc
        self.clientIDtoItem = {}
        self.wrappedHandlers = {}

    def _addChild(self, rowLabels, item):
        ti = xul.TreeItem()
        self.clientIDtoItem[str(ti.id)] = item
        tr = xul.TreeRow()
        for label in rowLabels:
            tr.append(xul.TreeCell(label=str(label)))
        ti.append(tr)
        self.treeChildren.append(ti)

    def notifySet(self, items):
        self.treeChildren.clear()
        self.clientIDtoItem = {}
        self.notifyAppend(items)

    def notifyAppend(self, items):
        for item, rowLabels in items:
            self._addChild(rowLabels, item)

    def notifyRemove(self, items):
        for item in items:
            for id, value in self.clientIDtoItem.items():
                if item == value:
                    child = self.treeChildren.getChild(id)
                    self.treeChildren.remove(child)
                    del self.clientIDtoItem[id]
                    break

    def addHandler(self, event, handler, *js):
        if event in ["ondblclick", "onselect"]:
            self.wrappedHandlers[event] = handler
            js = [livepage.js.TreeGetSelected(self.tree.id)] + list(js)
            self.tree.addHandler(event,
                lambda id, e=event, s=self, *a: s.onWrappedEvent(e, id, *a),
                *js)
        else:
            self.tree.addHandler(event, handler, *js)

    def onWrappedEvent(self, event, id, *args):
        self.wrappedHandlers[event](self.clientIDtoItem[id], *args)

    def getSelection(self):
        def _cbTreeGetSelection(result):
            if not result: return []
            return [self.clientIDtoItem[id] for id in result.split(',')]

        d = Deferred()
        getter = self.pageCtx.client.transient(lambda ctx, r: d.callback(r))
        self.pageCtx.client.send(getter(livepage.js.TreeGetSelected(
            self.tree.id)))
        d.addCallback(_cbTreeGetSelection)
        return d


class NestedTree(CompositeTreeBase):
    def __init__(self, agent, headerLabels, **kwargs):

        self.agent = agent

        t = xul.Tree(
            seltype="single",
            onclick="NestedTreeLoadSubTree(this, event, true);",
            ondblclick="NestedTreeLoadSubTree(this, event, false);",
            **kwargs)
        self.tree = t

        t.addHandler('onloadsubtree', self.onLoadSubTree)

        th = xul.TreeCols()
        for label in headerLabels:
            th.append(xul.TreeCol(flex=1, label=label, primary="true"))
        t.append(th)

        t.loaded = False
        t.segments = []
        t.subtree = {}

        self.idToNode = {}

        self.loadNode(self.tree)

    def addHandler(self, event, handler, *js):
        if event == "onselect":
            self._onSelectHandler = handler
            js = [livepage.js.TreeGetSelected(self.tree.id)] + list(js)
            self.tree.addHandler("onselect", self.onSelect, *js)

    def _getTreeItem(self, segments):
        node = self.tree
        for segment in segments:
            if not node.loaded: self.loadNode(node)
            node = node.subtree[segment]
        return node

    def selectBranch(self, segments):
        client = self.pageCtx.client
        if not len(segments):
            client.send(livepage.js.TreeSelectionClear(self.tree.id))
        else:
            node = self._getTreeItem(segments)
            client.send(livepage.js.TreeSelectionSet(self.tree.id, node.id))

    def loadNode(self, node):
        if not node.loaded:
            children = self.agent.getChildren(node.segments)
            if len(children):
                if node.alive: node.setAttr("open", "true")
                tc = xul.TreeChildren()
                for (path, empty, colLabels) in children:
                    ti = xul.TreeItem(container="true",
                        open="false", empty=empty)
                    tr = xul.TreeRow()
                    for label in colLabels:
                        tr.append(xul.TreeCell(label=label))
                    ti.append(tr)

                    self.idToNode[str(ti.id)] = ti

                    ti.loaded = False
                    ti.segments = node.segments + [path]
                    ti.subtree = {}

                    tc.append(ti)

                    node.subtree[path] = ti
                node.append(tc)
            node.loaded = True

    def onLoadSubTree(self, itemid):
        node = self.idToNode[itemid]
        self.loadNode(node)

    def onSelect(self, id):
        self._onSelectHandler(self.idToNode[id].segments)
