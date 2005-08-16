from twisted.internet.defer import gatherResults, Deferred

from nevow import livepage
from nufox import xul

class XULTKPage(xul.XULPage):

    def __init__(self):
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

        b = xul.Button(label="Add New Person")
        b.addHandler('oncommand', self.buttonAdd)
        hbox.append(b)

        b = xul.Button(label="Delete Selected")
        b.addHandler('oncommand', self.buttonDelete)
        hbox.append(b)

        v.append(hbox)

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
                ti = xul.TreeItem(value=row[0])
                tr = xul.TreeRow()
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


    def buttonAdd(self):
        def _cbButtonAdd(result):
            ti = xul.TreeItem()
            tr = xul.TreeRow()
            for cell in result:
                tr.append(xul.TreeCell(label=str(cell)))
            ti.append(tr)
            self.treeChildren.append(ti)

        d1 = self.nameTextBox.getAttr('value')
        d2 = self.ageTextBox.getAttr('value')
        dlist = gatherResults([d1, d2])
        dlist.addBoth(log)
        dlist.addCallback(_cbButtonAdd)

    """
    this will go in a tree composite soon
    just brain dumping for the moment
    """
    def getTreeSelection(self):
        def _cbTreeGetSelection(result):
            """result.split('.') - WTF livepage!"""
            result = [self.treeChildren.getChild(id) for id in result.split(',')]
            return result

        d = Deferred()
        getter = self.client.transient(lambda ctx, r: d.callback(r))
        self.client.send(getter(livepage.js.TreeGetSelected(self.tree.id)))
        d.addCallback(_cbTreeGetSelection)
        return d

    def treeSelect(self):
        self.getTreeSelection().addBoth(log)

    def buttonDelete(self):
        def _cbButtonDelete(result):
            self.treeChildren.remove(*result)
        self.getTreeSelection().addCallback(_cbButtonDelete)

def log(r):
    print "LOGGING ",r
    return r

example = XULTKPage()
