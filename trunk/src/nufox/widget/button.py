from nufox.widget.base import Signal, Widget
from nufox import xul


class Button(xul.Button, Widget):
    """Widget based on xul.Button"""

    class clicked(Signal):
        """The button was clicked."""
        args = ()

    def __init__(self, label=u''):
        xul.Button.__init__(self, label=label)
        Widget.__init__(self)
        self.addHandler('oncommand', self.handle_oncommand)

    def handle_oncommand(self):
        self.dispatch(self.clicked)
