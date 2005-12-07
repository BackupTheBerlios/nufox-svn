from nufox.defer import defgen, wait

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

    @defgen
    def handle_oncommand(self):
        yield wait(self.dispatch(self.clicked))
        yield None

    @defgen
    def enabled(self):
        disabled = wait(self.getAttr('disabled'))
        yield disabled
        disabled = disabled.getResult()
        yield result.lower() != u'true'

    @defgen
    def setEnabled(self, enabled):
        if enabled:
            disabled = u''
        else:
            disabled = u'true'
        yield wait(self.setAttr('disabled', disabled))
        yield enabled
