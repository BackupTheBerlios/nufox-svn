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

class SimpleTree(xul.GenericWidget):
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

    def __getattr__(self, name):
        """
        delegate most of genericwidget's interface to our tree widget
        """
        if name in [
            'children', 'id', 'pageCtx', 'rend', 'rendPostLive',
            'addHandler', 'handlers', 'getTag'
        ]:
            return getattr(self.tree, name)
        # XXX - Fix Please
        raise AttributeError, name
