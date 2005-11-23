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

    def setValue(self, value):
        def valueSet(result):
            self.dispatch(self.changed, value)
            return value
        return self.setAttr(u'value', value).addCallback(valueSet)

