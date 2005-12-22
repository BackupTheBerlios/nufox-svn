from nufox.defer import defgen, wait
from nufox.functional import partial
from nufox.widget.window import Window
from nufox.widget import signal, std
from nufox import xul


class CustomMenuItem(std.MenuItem):

    def preInit(self, kwargs):
        self._name = kwargs.pop('name')
        return super(CustomMenuItem, self).preInit(kwargs)

    def setup(self):
        super(CustomMenuItem, self).setup()
        self.set('value', self.id)
        self._counter = 0

    def counterMessage(self):
        self._counter += 1
        return u'You have selected "%s" %i times.' % (
            self._name, self._counter)


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
        # Spacer.
        vbox.append(std.VBox(height=50))
        # Custom menu item class usage.
        menuList2 = vbox.adopt(std.MenuList())
        menuPopup2 = menuList2.adopt(std.MenuPopup())
        menuPopup2.append(
            CustomMenuItem(label=u'My name is "fred"', name=u'fred'),
            CustomMenuItem(label=u'My name is "bork"', name=u'bork'),
            CustomMenuItem(label=u'My name is "yerk"', name=u'yerk'),
            )
        menuList2.connect(signal.itemSelected, self.on_menuList2_itemSelected)
        label2 = self.label2 = vbox.adopt(
            std.Label(value=u'This label will contain a counter.'))

    def on_menuList_itemSelected(self, value):
        self.label.set('value', u'The selected value was "%s"' % value)

    def on_menuList2_itemSelected(self, value):
        # Get the widget associated with the value, which in this case
        # is a widget ID.
        menuItem = self.id_widget[value]
        self.label2.set('value', menuItem.counterMessage())
