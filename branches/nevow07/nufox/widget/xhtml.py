from nufox.widget.base import Widget
from nufox.xul import htmlns


class Xhtml(Widget):

    namespace = htmlns

    def __init__(self, tag, *args, **kwargs):
        self.tag = tag
        Widget.__init__(self, *args, **kwargs)

    

