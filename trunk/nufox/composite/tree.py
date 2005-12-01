"""Nufox tree widgets."""

from twisted.internet.defer import Deferred

from nufox import xul


# Register Javascript.
xul.XULPage.globalJsIncludes.append('tree.js')


class Base(xul.GenericWidget):
    """Base class for tree widgets."""
    
    def __getattr__(self, name):
        # Delegate most of genericwidget's interface to our tree
        # widget.
        if name in [
            'addHandler',
            'children',
            'getTag',
            'handlers',
            'id',
            'kwargs',
            'pageCtx',
            'rend',
            'tag',
            ]:
            return getattr(self.tree, name)
        raise AttributeError, name


class Flat(Base):
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
            th.append(xul.Splitter(_class=u"tree-splitter"))
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
        mapper = self.mapper
        to_append = []
        for item in items:
            rowLabels = mapper(item)
            ti = xul.TreeItem()
            self.clientIDtoItem[str(ti.id)] = item
            tr = xul.TreeRow()
            for label in rowLabels:
                tr.append(xul.TreeCell(label=label))
            ti.append(tr)
            to_append.append(ti)
        return self.treeChildren.liveAppend(*to_append)

    def set(self, items):
        """Reset the tree children, and return a deferred that calls
        back when the last item in `items` is appended to the tree."""
        d = self.treeChildren.clear()
        def done(result):
            self.clientIDtoItem = {}
            return self._addChildren(*items)
        d.addCallback(done)
        return d

    def append(self, *items):
        """Return a deferred that calls back when the last item in
        `items` is appended to the tree."""
        return self._addChildren(*items)

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


# XXX: Not yet working:

## class FlatView(Base):
##     """Tree widget for a 1-tier list of items that loads data on
##     demand.

##     @param headerLabels: a tuple of strings for the tree's
##     column headers.

##     @param rowCount: number of rows in the tree.

##     @param kwargs: kwargs to configure the actual xul.Tree widget
##     """

##     def __init__(self, headerLabels, rowCount, **kwargs):
##         t = xul.Tree(**kwargs)
##         th = xul.TreeCols()
##         for cell in headerLabels:
##             th.append(xul.TreeCol(flex=1, label=cell))
##             th.append(xul.Splitter(_class=u"tree-splitter"))
##         t.append(th)
##         tc = xul.TreeChildren()
##         t.append(tc)
##         self.tree = t
##         self.treeChildren = tc
##         self.clientIDtoItem = {}
##         self.wrappedHandlers = {}
##         # Set up the view on the remote side.
##         from twisted.internet import reactor
##         reactor.callLater(
##             0, lambda : self.pageCtx.callRemote('FlatTreeSetView',
##                                                 t.id, rowCount))

##     def remote_getCellText(self, row, col):
##         """Return text for the given row and column.

##         Override this in your FlatView subclass.
##         """
##         return u''


class Nested(Base):

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
            th.append(xul.TreeCol(flex=1, label=label, primary=u"true"))
        t.append(th)

        t.loaded = False
        t.segments = []
        t.subtree = {}

        self.idToNode = {}

        self.loadNode(self.tree)

    def addHandler(self, event, handler, *js):
        if event == "onselect":
            self._onSelectHandler = handler
            # XXX: Update to use athena.
##             js = [livepage.js.TreeGetSelected(self.tree.id)] + list(js)
##             self.tree.addHandler("onselect", self.onSelect, *js)

    def _getTreeItem(self, segments):
        node = self.tree
        for segment in segments:
            if not node.loaded: self.loadNode(node)
            node = node.subtree[segment]
        return node

    def selectBranch(self, segments):
        client = self.pageCtx.client
        # XXX: Update to use athena.
##         if not len(segments):
##             client.send(livepage.js.TreeSelectionClear(self.tree.id))
##         else:
##             node = self._getTreeItem(segments)
##             client.send(livepage.js.TreeSelectionSet(self.tree.id, node.id))

    def loadNode(self, node):
        if not node.loaded:
            children = self.abstraction.getChildren(node.segments)
            if len(children):
                if node.alive: node.setAttr("open", u"true")

                if hasattr(node, "treeChildrenNode"):
                    tc = node.treeChildrenNode
                else:
                    tc = xul.TreeChildren()

                for (path, empty, colLabels) in children:
                    ti = xul.TreeItem(container=u"true",
                        open=u"false", empty=empty)
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
