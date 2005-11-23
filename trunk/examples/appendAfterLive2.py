from twisted.internet.defer import gatherResults

from nufox import xul


class Example(xul.XULPage):
    """Append After Live 2

    Appends nodes after going live.
    """

    def setup(self):
        self.window = xul.Window(id=u"xul-window", height=400, width=400,
                                 title=u"XUL is Cool")
        v = xul.GroupBox(flex=1)
        self.box = v

        v.append(xul.Caption(label=u"Fun with Trees"))

        hbox = xul.HBox()
        hbox.append(xul.Label(value=u"Name:"))
        self.nameTextBox = xul.TextBox(value=u'Henry')
        hbox.append(self.nameTextBox)
        hbox.append(xul.Label(value=u"Age:"))
        self.ageTextBox = xul.TextBox(value=u'43')
        hbox.append(self.ageTextBox)
        v.append(hbox)

        b = xul.Button(label=u"The Give Me More Button")
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

        t,tc = listToTree([(u"Name", u"Age"),
            (u"ned", 23),
            (u"fred", 35),
            (u"ted", 52),])

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
        d1 = self.nameTextBox.getAttr(u'value')
        d2 = self.ageTextBox.getAttr(u'value')
        dlist = gatherResults([d1, d2])
        dlist.addBoth(log)
        dlist.addCallback(self._cbButtonPushed)

    def treeSelect(self):
        self.tree.getAttr(u'value').addBoth(log)


def log(r):
    print "LOGGING ",r
    return r
