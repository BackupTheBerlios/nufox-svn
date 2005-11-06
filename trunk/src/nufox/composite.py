"""Nufox composite widgets.

Composite widgets manage collections of XUL elements for you. They
expose higher-level methods on the Python side, and reduce round trips
by using custom JavaScript on the XUL side.
"""

from nevow import livepage

from nufox import xul


class Grid(xul.GenericWidget):
    """Render a list of lists of XUL widgets into a grid.

    The grid is length of list by length of the longest list. Shorter
    lists will be padded with xul.Spacer() widgets.
    """

    def __init__(self, l):
        xul.GenericWidget.__init__(self)
        self.data = l
        self.width = 0
        for l in self.data:
            if len(l) > self.width:
                self.width = len(l)

    def getTag(self):
        grid = xul.Grid()
        columns = xul.Columns()
        rows = xul.Rows()
        for i in range(self.width):
            columns.append(xul.Column())
        for l in self.data:
            if len(l) < self.width:
                for i in range(self.width - len(l)):
                    l.append(xul.Spacer())
            rows.append(xul.Row().append(*l))
        grid.append(columns, rows)
        return grid

class Player(xul.GenericWidget):
    """Helix/RealPlayer-based media player.

    Requires Helix or RealPlayer plugin to be installed in Mozilla."""

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


class CompositeTreeBase(xul.GenericWidget):
    """Base class for tree widgets."""
    
    def __getattr__(self, name):
        # Delegate most of genericwidget's interface to our tree
        # widget.
        if name in [
            'children', 'id', 'pageCtx', 'rend',
            'addHandler', 'handlers', 'getTag'
            ]:
            return getattr(self.tree, name)
        raise AttributeError, name


class SimpleTree(CompositeTreeBase):
    """Simple tree widget for a 1-tier list of items.

    @param headerLabels: a tuple of strings for the tree's
    column headers.

    @param mapper: a function which maps an item to the
    column values for the tree row which will represent that
    item

    @param kwargs: kwargs to configure the actual xul.Tree widget
    """

    def __init__(self, headerLabels, mapper, items=None, **kwargs):
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

        self.mapper = mapper
        if items: self.set(items)

    def _addChildren(self, *items):
        for item in items:
            rowLabels = self.mapper(item)
            print rowLabels
            ti = xul.TreeItem()
            self.clientIDtoItem[str(ti.id)] = item
            tr = xul.TreeRow()
            for label in rowLabels:
                tr.append(xul.TreeCell(label=label))
            ti.append(tr)
            self.treeChildren.liveAppend(ti)

    def set(self, items):
        self.treeChildren.clear()
        self.clientIDtoItem = {}
        self._addChildren(*items)

    def append(self, *items):
        self._addChildren(*items)

    def remove(self, items):
        childrenToDelete = []
        for item in items:
            for id, value in self.clientIDtoItem.items():
                if item == value:
                    child = self.treeChildren.getChild(id)
                    childrenToDelete.append(child)
                    del self.clientIDtoItem[id]
                    break
        return self.treeChildren.remove(*childrenToDelete)

    def addHandler(self, event, handler, *args):
        if event in ["ondblclick", "onselect"]:
            self.wrappedHandlers[event] = handler
            args = [
                xul.requestFunction("TreeGetSelected", self.tree.id)
            ] + list(args)
            self.tree.addHandler(event,
                lambda id, e=event, s=self, *a: s.onWrappedEvent(e, id, *a),
                *args)
        else:
            self.tree.addHandler(event, handler, *args)

    def onWrappedEvent(self, event, id, *args):
        self.wrappedHandlers[event](self.clientIDtoItem[id[0]], *args)

    def idsToItems(self, ids):
        return [self.clientIDtoItem[id] for id in ids]

    def getSelection(self):
        def _cbTreeGetSelection(result):
            ids = result[0][0]
            if not ids: return []
            return self.idsToItems(ids)
        d = self.pageCtx.callRemote("TreeGetSelected", self.tree.id)
        d.addCallback(_cbTreeGetSelection)
        return d


class NestedTree(CompositeTreeBase):

    def __init__(self, abstraction, headerLabels, **kwargs):
        self.abstraction = abstraction

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
            children = self.abstraction.getChildren(node.segments)
            if len(children):
                if node.alive: node.setAttr("open", "true")

                if hasattr(node, "treeChildrenNode"):
                    tc = node.treeChildrenNode
                else:
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
                node.treeChildrenNode = tc
            node.loaded = True

    """XXX - this isn't right at all, still working out how to do it"""
    def reloadNode(self, node):
        if node.loaded:
            node.treeChildrenNode.remove(*node.treeChildrenNode.children)
            node.loaded = False
            self.loadNode(node)

    def reloadBranch(self, segments):
        node = self._getTreeItem(segments)
        self.reloadNode(node)

    def onLoadSubTree(self, itemid):
        node = self.idToNode[itemid]
        self.loadNode(node)

    def onSelect(self, id):
        if id: self._onSelectHandler(self.idToNode[id].segments)
