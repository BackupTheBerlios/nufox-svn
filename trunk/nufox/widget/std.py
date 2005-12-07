from twisted.internet.defer import succeed

from nufox.defer import defgen, wait
from nufox.widget.base import Widget
from nufox.widget import signal
from nufox.xul import bigListOXulTags


def _to_bool(value):
    return value.lower() == u'true'

def _from_bool(value):
    return unicode(value).lower()

def _from_int_or_zero(value):
    if value:
        return int(value)
    return 0


class Standard(Widget):

    def __init__(self, **kwargs):
        h = self.__handlers = {}
        if kwargs.pop('jsOnclick', True):
            h['onclick'] = self.__handle_onclick
        if kwargs.pop('jsOncommand', True):
            h['oncommand'] = self.__handle_oncommand
        Widget.__init__(self, **kwargs)

    def preSetup(self):
        for jsEvent, handler in self.__handlers.iteritems():
            self.addHandler(jsEvent, handler)

    @defgen
    def __handle_onclick(self):
        yield wait(self.dispatch(signal.jsOnclick))
        yield None

    @defgen
    def __handle_oncommand(self):
        yield wait(self.dispatch(signal.jsOncommand))
        yield None

    # Make ``disabled`` a bool.

    def postGet_disabled(self, value):
        return succeed(_to_bool(value))

    def preSet_disabled(self, value):
        return succeed(('disabled', _from_bool(value)))

    # At times it's handy to think of it as ``enabled`` instead.

    def preGet_enabled(self):
        return succeed('disabled')

    def postGet_enabled(self, value):
        return succeed(not _to_bool(value))

    def preSet_disabled(self, value):
        return succeed(('disabled', _from_bool(not value)))


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

    def setup(self):
        self.connect(signal.jsOncommand, self.on_jsOncommand)

    @defgen
    def on_jsOncommand(self):
        yield wait(self.dispatch(signal.clicked))
        yield None


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
        return self.dispatch(signal.changed, value)
