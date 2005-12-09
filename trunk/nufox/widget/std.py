from twisted.internet.defer import succeed

from nufox.defer import defgen, wait
from nufox.widget.base import Widget
from nufox.widget import signal
from nufox.xul import bigListOXulTags


def _to_bool(value):
    return str(value).lower() == 'true'

def _from_bool(value):
    if value:
        return u'true'
    else:
        return u''

def _from_int_or_zero(value):
    if value:
        return int(value)
    return 0


class Standard(Widget):

    def __init__(self, **kwargs):
        h = self.__handlers = {}
        if kwargs.pop('jsOnclick', False):
            h['onclick'] = self.__handle_onclick
        if kwargs.pop('jsOndblclick', False):
            h['ondblclick'] = self.__handle_ondblclick
        if kwargs.pop('jsOncommand', False):
            h['oncommand'] = self.__handle_oncommand
        Widget.__init__(self, **kwargs)

    def preSetup(self):
        for jsEvent, handler in self.__handlers.iteritems():
            self.addHandler(jsEvent, handler)

    def __handle_onclick(self):
        self.dispatch(signal.jsOnclick)

    def __handle_ondblclick(self):
        self.dispatch(signal.jsOndblclick)

    def __handle_oncommand(self):
        self.dispatch(signal.jsOncommand)

    # Make ``disabled`` a bool.

    def postGet_disabled(self, value):
        return _to_bool(value)

    def preSet_disabled(self, value):
        return ('disabled', _from_bool(value))

    # At times it's handy to think of it as ``enabled`` instead.

    def preGet_enabled(self):
        return 'disabled'

    def postGet_enabled(self, value):
        return not _to_bool(value)

    def preSet_enabled(self, value):
        return ('disabled', _from_bool(not value))

    # Make ``collapsed`` a bool.

    def postGet_collapsed(self, value):
        return _to_bool(value)

    def preSet_collapsed(self, value):
        return ('collapsed', _from_bool(value))


g = globals()
for t in bigListOXulTags:
    if t not in g:
        g[t] = type(t, (Standard,), {'tag': t.lower()})


_Button = Button
class Button(_Button):
    """Push button.

    Dispatches:

    - `nufox.widget.signal.clicked` when the button is clicked.
    """

    def __init__(self, **kwargs):
        kwargs['jsOncommand'] = True
        super(Button, self).__init__(**kwargs)

    def setup(self):
        self.connect(signal.jsOncommand, self.on_jsOncommand)

    def on_jsOncommand(self):
        self.dispatch(signal.clicked)


_Deck = Deck
class Deck(_Deck):
    """Deck.

    Attributes:

    - ``selectedPage`` can be used to get the actual widget
      corresponding to the ``selectedIndex``.

    Dispatches:

    - `nufox.widget.signal.pageSelected` when the deck's page was
      changed.
    """

    def postGet_selectedIndex(self, value):
        return succeed(_from_int_or_zero(value))

    def preGet_selectedPage(self):
        return succeed('selectedIndex')

    def postGet_selectedPage(self):
        return succeed(self.children.index(page))

    def preSet_selectedPage(self, page):
        index = self.children.index(page)
        return succeed(('selectedIndex', index))

    @defgen
    def addPage(self, page):
        """Returns the index of ``page`` after adding it."""
        yield wait(self.liveAppend(page))
        yield self.children.index(page)

    def removePage(self, page):
        """Removes the ``page`` child."""
        return self.remove(page)

    def indexOfPage(self, page):
        return self.children.index(page)

    def indexToPage(self, index):
        return self.children[index]
    

_Label = Label
class Label(_Label):
    """Label.

    Dispatches:

    - `nufox.widget.signal.changed` when the ``value`` attribute is changed.
    """

    def postSet_value(self, value):
        self.dispatch(signal.changed, value)
