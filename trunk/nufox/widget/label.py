from nufox.defer import defgen, wait

from nufox.widget.base import Signal, Widget
from nufox import xul


class Label(Widget):
    """Label."""

    tag = 'label'

    class changed(Signal):
        """The label's value was changed."""
        args = ('value', )

    def __init__(self, **kwargs):
        Widget.__init__(self, **kwargs)

    def value(self):
        return self.getAttr(u'value')

    @defgen
    def setValue(self, value):
        yield wait(self.setAttr('value', value))
        yield wait(self.dispatch(self.changed, value))
        yield value

