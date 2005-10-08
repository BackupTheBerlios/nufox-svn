from nevow import livepage
from nufox import xul

class Example(xul.XULPage):

    def __init__(self):
        self.counter = 0
        self.window = xul.Window(id="xul-window", height=400, width=400,
                                 title="XUL is Cool")
        v = xul.VBox(flex=1)

        ml = xul.MenuList()
        mp = xul.MenuPopup()
        mp.append(xul.MenuItem(label='the value that be fred', value='fred'))
        mp.append(xul.MenuItem(label='the value that be bork', value='bork'))
        mp.append(xul.MenuItem(label='the value that be yerk', value='yerk'))
        ml.append(mp)
        ml.addHandler('oncommand', self.menuSelect)
        self.menuList = ml
        v.append(self.menuList)

        self.label = xul.Label(value='hello there')
        v.append(self.label)

        self.window.append(v)

    def menuSelect(self):
        d = self.menuList.getAttr('value')
        d.addBoth(log)
        d.addCallback(lambda r, s:
                s('value', 'you chose: %s' % r),
            self.label.setAttr)

def log(r):
    print "LOGGING ",r
    return r

