from nufox.widget.base import Signal, Widget
from nufox import xul


class Label(xul.Label, Widget):
    """Widget based on xul.Button"""

    class changed(Signal):
        """The label's value was changed."""
        args = ('value', )

    def __init__(self, value=u''):
        xul.Label.__init__(self, value=value)
        Widget.__init__(self)

    def value(self):
        return self.getAttr(u'value')

    def setValue(self, value):
        print 'setting value of', self, 'to', value
        def valueSet(result):
            self.dispatch(self.changed, value)
            return value
        return self.setAttr(u'value', value)

