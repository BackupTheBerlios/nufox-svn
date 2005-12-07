from nufox.defer import defgen, wait
from twisted.internet.defer import DeferredList

from nufox.widget import signal, std


class ItemGrid(std.Grid):
    """Grid suited towards displaying mostly homogeneous lists of
    items."""

    HORIZONTAL, VERTICAL = range(2)

    def preInit(self, kwargs):
        self.orientation = kwargs.pop('orientation', self.VERTICAL)

    def setup(self):
        columns = self.columns = std.Columns()
        rows = self.rows = std.Rows()
        if self.orientation is self.VERTICAL:
            self.append(columns, rows)
            self.headingWidgets = rows.adopt(std.Row())
            self.headingClass = std.Column
            self.headingContainer = columns
            self.itemWidgets = rows
            self.itemClass = std.Row
        elif self.orientation is self.HORIZONTAL:
            self.append(rows, columns)
            self.headingWidgets = columns.adopt(std.Column())
            self.headingClass = std.Row
            self.headingContainer = rows
            self.itemWidgets = columns
            self.itemClass = std.Column

    @defgen
    def addHeading(self, widget, **kwargs):
        """Add `widget` as the next column or row heading, depending
        on the orientation."""
        yield wait(DeferredList([
            self.headingContainer.liveAppend(self.headingClass(**kwargs)),
            self.headingWidgets.liveAppend(widget),
            ]))
        yield widget
        
    def addItem(self, *widgets, **kwargs):
        """Add `widgets` as the next item row or column, depending on
        the orientation."""
        return self.itemWidgets.liveAppend(
            self.itemClass(**kwargs).append(*widgets))
