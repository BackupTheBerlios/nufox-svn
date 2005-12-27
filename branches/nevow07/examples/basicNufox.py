from nufox import xul


class Example(xul.XULPage):
    """Basic nufox"""

    def setup(self):
        self.counter = 0
        self.window = xul.Window(id=u"xul-window", height=400, width=400,
                                 title=u"Press this button!")
        v = xul.VBox(flex=1)
        b = xul.Button(label=u"A Button")
        b.addHandler('oncommand', self.buttonPushed)
        self.label = xul.Label(value=u'hello there')
        v.append(b)
        v.append(self.label)
        self.window.append(v)

    def buttonPushed(self, *args):
        print args
        self.counter += 1
        self.label.setAttr(u'value',
            u'You have clicked %s times' % ( self.counter,))
        d = self.label.getAttr(u'value')
        d.addBoth(log)


def log(r):
    print "LOGGING ",r

