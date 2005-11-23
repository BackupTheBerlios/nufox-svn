from twisted.internet.defer import DeferredList

from nufox.widget.base import Signal, Widget
from nufox.widget.splitter import Splitter
from nufox import xul


# Register Javascript.
xul.XULPage.widgetJsIncludes.append('listbox.js')


class ListBox(Widget):
    """List box."""

    tag = 'listbox'

    class selected(Signal):
        """A list box item was selected."""
        args = ('item', )

    def setup(self):
        self.widgetItem = {}
        # Handle selection.
        self.addHandler('onselect', self.handle_onselect)

    def addColumn(self, label):
        L = []
        children = self.children
        # Get list columns.
        if not children or children[0].tag != 'ListCols':
            # Initialize list columns.
            listCols = xul.ListCols()
            listHead = xul.ListHead()
            if not children:
                L.append(self.liveAppend(listCols, listHead))
            else:
                L.append(self.liveInsert(children[0], listCols, listHead))
        else:
            listCols = self.children[0]
            listHead = self.children[1]
        # Add a splitter if necessary.
        newCols = []
        newHeaders = []
        if listCols.children:
            newCols.append(Splitter(class_=u'tree-splitter'))
        L.append(listCols.liveAppend(xul.ListCol(flex=1)))
        L.append(listHead.liveAppend(xul.ListHeader(label=label)))
        return DeferredList(L)

    def addItem(self, item):
        listItem = item.widget()
        self.widgetItem[listItem] = item
        return self.liveAppend(listItem)

    def handle_onselect(self):
        pageCtx = self.pageCtx
        d = pageCtx.callRemote('ListBoxGetSelectedId', self.id)
        def gotId(listItemId):
            listItemId = listItemId[0][0]
            listItem = pageCtx.id_widget[listItemId]
            item = self.widgetItem[listItem]
            self.dispatch(self.selected, item)
        d.addCallback(gotId)


class ListBoxItem(object):
    """Metadata about a ListBox item."""

    def __init__(self, *values):
        self.values = values
        self.listItem = None

    def widget(self):
        if self.listItem:
            return self.listItem
        listItem = self.listItem = xul.ListItem()
        for value in self.values:
            listItem.append(xul.Label(value=value))
        return listItem
