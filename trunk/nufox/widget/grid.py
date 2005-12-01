from twisted.internet.defer import DeferredList

from nufox.widget.base import Signal, Widget
from nufox import xul


class Grid(Widget):
    """Grid."""

    tag = 'grid'


class ItemGrid(Grid):
    """Grid suited towards displaying mostly homogeneous lists of
    items."""

    HORIZONTAL, VERTICAL = range(2)

    def preSetup(self, kwargs):
        self.orientation = kwargs.pop('orientation', self.VERTICAL)

    def setup(self):
        columns = self.columns = xul.Columns()
        rows = self.rows = xul.Rows()
        if self.orientation is self.VERTICAL:
            self.append(columns, rows)
            self.headingWidgets = rows.adopt(xul.Row())
            self.headingClass = xul.Column
            self.headingContainer = columns
            self.itemWidgets = rows
            self.itemClass = xul.Row
        elif self.orientation is self.HORIZONTAL:
            self.append(rows, columns)
            self.headingWidgets = columns.adopt(xul.Column())
            self.headingClass = xul.Row
            self.headingContainer = rows
            self.itemWidgets = columns
            self.itemClass = xul.Column

    def addHeading(self, widget, **kwargs):
        """Add `widget` as the next column or row heading, depending
        on the orientation."""
        d = DeferredList([
            self.headingContainer.liveAppend(self.headingClass(**kwargs)),
            self.headingWidgets.liveAppend(widget),
            ])
        def returnWidget(result):
            return widget
        return d.addCallback(returnWidget)
        
    def addItem(self, *widgets, **kwargs):
        """Add `widgets` as the next item row or column, depending on
        the orientation."""
        return self.itemWidgets.liveAppend(
            self.itemClass(**kwargs).append(*widgets))
