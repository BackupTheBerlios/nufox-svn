from nufox.widget.base import Signal, Widget
from nufox import xul


class Button(Widget):
    """Button."""

    tag = 'button'

    class clicked(Signal):
        """The button was clicked."""
        args = ()

    def preSetup(self, kwargs):
        enabled = kwargs.pop('enabled', True)
        kwargs['disabled'] = unicode(not enabled).lower()

    def setup(self):
        self.addHandler('oncommand', self.handle_oncommand)

    def handle_oncommand(self):
        self.dispatch(self.clicked)

    def enabled(self):
        d = self.getAttr('disabled')
        def invert(result):
            return result.lower() != u'true'
        return d

    def setEnabled(self, enabled):
        if enabled:
            disabled = u''
        else:
            disabled = u'true'
        def returnEnabled(result):
            return enabled
        return self.setAttr('disabled', disabled).addCallback(returnEnabled)
