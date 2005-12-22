from nufox.defer import defgen, wait
from nufox.functional import partial
from nufox.widget.window import Window
from nufox.widget import signal, std
from nufox import xul


class Example(xul.XULPage):
    """nufox.widget: MenuList usage"""

    def setup(self):
        # Create the window.
        window = self.window = Window(title=u'MenuList usage')
        # Create a box to layout our widgets.
        vbox = window.adopt(std.VBox(flex=1))
        # Create a menu list.
        menuList = vbox.adopt(std.MenuList())
        menuPopup = menuList.adopt(std.MenuPopup())
        menuPopup.append(
            std.MenuItem(label=u'My value is "fred"', value=u'fred'),
            std.MenuItem(label=u'My value is "bork"', value=u'bork',
                         selected=True),
            std.MenuItem(label=u'My value is "yerk"', value=u'yerk'),
            )
        # Connect the itemSelected signal.
        menuList.connect(signal.itemSelected, self.on_menuList_itemSelected)
        # Create a label to show the value.
        label = self.label = vbox.adopt(
            std.Label(value=u'This label will contain the selected value.'))

    def on_menuList_itemSelected(self, value):
        self.label.set('value', u'The selected value was "%s"' % value)
