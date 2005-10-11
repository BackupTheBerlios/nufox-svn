from nevow import livepage
from nufox import xul

class Example(xul.XULPage):

    def setup(self):
        self.counter = 0
        self.window = xul.Window(id="xul-window", height=400, width=400,
                                 title="A tree")

        self.tree = xul.Tree(flex=3)
        cols = xul.TreeCols()
        cols.append(xul.TreeCol(label='Thingo', primary='true', flex=3))
        self.tree.append(cols)

        def addChild(parent, childlabel):
            item = xul.TreeItem(container='true', open='true')
            row = xul.TreeRow()
            row.append(xul.TreeCell(label=childlabel))
            item.append(row)
            parent.append(item)
            return item

        children = xul.TreeChildren()
        for child in "tjs radix teratorn mika simon kev ross sam".split():
            item = addChild(children, child)
            if child == 'radix':
                radchildren = xul.TreeChildren()
                addChild(radchildren, "IS COOL")
                item.append(radchildren)
        self.tree.append(children)
        self.window.append(self.tree)

