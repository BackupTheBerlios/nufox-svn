from twisted.internet.defer import gatherResults

from nufox import xul


class Example(xul.XULPage):

    def setup(self):
        self.window = xul.Window(id="xul-window", height=400, width=400,
                                 title="XUL is Cool")
        v = xul.GroupBox(flex=1)
        self.box = v

        v.append(xul.Caption(label="Fun with Trees"))

        hbox = xul.HBox()
        hbox.append(xul.Label(value="Name:"))
        self.nameTextBox = xul.TextBox(value='Henry')
        hbox.append(self.nameTextBox)
        hbox.append(xul.Label(value="Age:"))
        self.ageTextBox = xul.TextBox(value='43')
        hbox.append(self.ageTextBox)
        v.append(hbox)

        b = xul.Button(label="The Give Me More Button")
        b.addHandler('oncommand', self.buttonPushed)
        v.append(b)

        def listToTree(list):
            t = xul.Tree(flex=1)

            header = list[0]
            list = list[1:]
            th = xul.TreeCols()
            for cell in header:
                th.append(xul.TreeCol(flex=1, label=cell))
            t.append(th)

            tc = xul.TreeChildren()
            for row in list:
                ti = xul.TreeItem()
                tr = xul.TreeRow(value=row[0])
                for cell in row:
                    tr.append(xul.TreeCell(label=str(cell)))
                ti.append(tr)
                tc.append(ti)

            t.append(tc)
            return (t,tc)

        t,tc = listToTree([("Name", "Age"),
            ("ned", 23),
            ("fred", 35),
            ("ted", 52),])

        t.addHandler('onselect', self.treeSelect)
        v.append(t)

        self.tree = t
        self.treeChildren = tc

        self.window.append(v)

    def _cbButtonPushed(self, result):
        ti = xul.TreeItem()
        tr = xul.TreeRow()
        for cell in result:
            tr.append(xul.TreeCell(label=cell))
        ti.append(tr)
        self.treeChildren.liveAppend(ti)

    def buttonPushed(self):
        d1 = self.nameTextBox.getAttr('value')
        d2 = self.ageTextBox.getAttr('value')
        dlist = gatherResults([d1, d2])
        dlist.addBoth(log)
        dlist.addCallback(self._cbButtonPushed)

    def treeSelect(self):
        self.tree.getAttr('value').addBoth(log)


def log(r):
    print "LOGGING ",r
    return r
