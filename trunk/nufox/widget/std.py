from twisted.internet.defer import succeed

from nufox.defer import defgen, wait
from nufox.widget.base import Widget
from nufox.widget import signal
from nufox.xul import bigListOXulTags


def _to_boolean(self, value):
    return succeed(value.lower() == u'true')

def _from_boolean(self, value):
    return succeed(unicode(value).lower())


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

    preSet_disabled = _from_boolean
    postGet_disabled = _to_boolean
            

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



_Label = Label
class Label(_Label):
    """Label.

    Dispatches:

    - `nufox.widget.signal.changed` when the ``value`` attribute is changed.
    """

    def postSet_value(self, value):
        return self.dispatch(signal.changed, value)
