from nufox.widget.base import Signal, Widget
from nufox import xul


class Splitter(Widget):
    """Splitter."""

    tag = 'splitter'

    def setup(self):
        if unicode(self.kwargs.get('collapse', u'none')) != u'none':
            self.adopt(xul.Grippy())
