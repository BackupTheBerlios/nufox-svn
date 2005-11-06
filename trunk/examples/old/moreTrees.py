from twisted.internet.defer import gatherResults

from nufox import composite, xul


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

        b = xul.Button(label="Add New Person")
        b.addHandler('oncommand', self.buttonAdd)
        hbox.append(b)

        b = xul.Button(label="Delete Selected")
        b.addHandler('oncommand', self.buttonDelete)
        hbox.append(b)
        v.append(hbox)

        self.tree = composite.SimpleTree(('Name', 'Age'), flex=1)
        self.tree.addHandler('onselect', self.treeSelect)

        self.people = composite.SequenceSubject([
            ("ned", 23), ("fred", 35), ("ted", 52)])
        self.people.addObserver(self.tree, lambda x: x)

        v.append(self.tree)

        self.window.append(v)

    def buttonAdd(self):
        def _cbButtonAdd(result):
            self.people.append(result)

        d1 = self.nameTextBox.getAttr('value')
        d2 = self.ageTextBox.getAttr('value')
        dlist = gatherResults([d1, d2])
        dlist.addBoth(log)
        dlist.addCallback(_cbButtonAdd)

    def treeSelect(self):
        self.tree.getSelection().addBoth(log)

    def buttonDelete(self):
        def _cbButtonDelete(result):
            self.people.remove(*result)
        self.tree.getSelection().addCallback(_cbButtonDelete)


def log(r):
    print "LOGGING ",r
    return r

