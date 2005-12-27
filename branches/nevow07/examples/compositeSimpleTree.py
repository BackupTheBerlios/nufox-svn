from nufox.composite import tree
from nufox import xul


class Person:

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __str__(self):
        return u"name: %s, age: %s" % (
            self.name, self.age)


class Example(xul.XULPage):
    """Composite Simple Tree (debug me)"""

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
        b.addHandler('oncommand', self.onAdd,
            self.nameTextBox.requestAttr(u'value'),
            self.ageTextBox.requestAttr(u'value'))
        v.append(b)

        b = xul.Button(label=u"The Give Me Less Button")
        b.addHandler('oncommand', self.onRemove)
        v.append(b)

        self.tree = tree.Flat(
            (u"Name", u"Age"),
            lambda x: (x.name, x.age),
            items=[
                Person(u"ned", 23),
                Person(u"fred", 35),
                Person(u"ted", 52)],
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
