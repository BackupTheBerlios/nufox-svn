"""Nufox grid widget."""

from nufox import xul


# Register Javascript.
xul.XULPage.globalJsIncludes.append('grid.js')


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


