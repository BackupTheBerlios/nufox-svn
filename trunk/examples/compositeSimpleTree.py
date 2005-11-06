from twisted.internet.defer import gatherResults

from nufox import xul, composite


class Person:

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __str__(self):
        return "name: %s, age: %s" % (
            self.name, self.age)


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
        b.addHandler('oncommand', self.onAdd,
            self.nameTextBox.requestAttr('value'),
            self.ageTextBox.requestAttr('value'))
        v.append(b)

        b = xul.Button(label="The Give Me Less Button")
        b.addHandler('oncommand', self.onRemove)
        v.append(b)

        self.tree = composite.SimpleTree(
            ("Name", "Age"),
            lambda x: (x.name, x.age),
            items=[
                Person("ned", 23),
                Person("fred", 35),
                Person("ted", 52)],
            flex=1)
        v.append(self.tree)
        self.tree.addHandler('ondblclick', self.onTreeDblClick)

        self.window.append(v)

    def onAdd(self, name, age):
        self.tree.append(Person(name, age))

    def onTreeDblClick(self, item):
        print "FROAR!"
        print "You Double Clicked Person: %s" % item
        print

    def onRemove(self):
        def _cb_onRemove(items):
            self.tree.remove(items)
        d = self.tree.getSelection()
        d.addCallback(_cb_onRemove)


def log(r):
    print "LOGGING ",r
    return r
