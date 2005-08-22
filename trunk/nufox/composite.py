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


class SimpleTree(xul.GenericWidget):
    """
    I'm a simple tree widget for a 1 tier list of items

    @param headerLabels: a tuple of strings for the tree's
    column headers.

    @param itemToRowLabels: a callable which takes an item
    and returns a tuple of strings to be used for the column
    labels for the tree row that represents that item.  the
    length of the tuple returned should be the same as headerLabels

    @param items: a list of items this tree widget will represent

    @param kwargs: kwargs to configure the actual xul.Tree widget
    """

    def __init__(self, headerLabels, itemToRowLabels, items=[], **kwargs):
        t = xul.Tree(**kwargs)
        th = xul.TreeCols()
        for cell in headerLabels:
            th.append(xul.TreeCol(flex=1, label=cell))
        t.append(th)
        tc = xul.TreeChildren()
        t.append(tc)
        self.tree = t
        self.treeChildren = tc
        self.itemToRowLabels = itemToRowLabels
        self.items = items
        self.updateClient()

    def updateClient(self):
        self.treeChildren.clear()
        self.clientIDtoItem = {}
        print self.items
        for item in self.items:
            rowLabels = self.itemToRowLabels(item)
            ti = xul.TreeItem()
            self.clientIDtoItem[str(ti.id)] = item
            tr = xul.TreeRow()
            for label in rowLabels:
                tr.append(xul.TreeCell(label=str(label)))
            ti.append(tr)
            self.treeChildren.append(ti)

    def getSelection(self):
        def _cbTreeGetSelection(result):
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
