from nufox import xul


class Example(xul.XULPage):
    """Basic Menu List"""

    def setup(self):
        self.counter = 0
        self.window = xul.Window(id=u"xul-window", height=400, width=400,
                                 title=u"XUL is Cool")
        v = xul.VBox(flex=1)

        ml = xul.MenuList()
        mp = xul.MenuPopup()
        mp.append(xul.MenuItem(label=u'the value that be fred', value=u'fred'))
        mp.append(xul.MenuItem(label=u'the value that be bork', value=u'bork'))
        mp.append(xul.MenuItem(label=u'the value that be yerk', value=u'yerk'))
        ml.append(mp)
        ml.addHandler('oncommand', self.menuSelect)
        self.menuList = ml
        v.append(self.menuList)

        self.label = xul.Label(value=u'hello there')
        v.append(self.label)

        self.window.append(v)

    def menuSelect(self):
        d = self.menuList.getAttr(u'value')
        d.addBoth(log)
        d.addCallback(lambda r, s:
                s(u'value', u'you chose: %s' % r),
            self.label.setAttr)


def log(r):
    print "LOGGING ",r
    return r

