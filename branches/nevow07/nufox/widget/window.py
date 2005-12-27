from nufox.defer import defgen, wait
from twisted.internet.defer import Deferred, DeferredList

from nufox.widget.base import Widget
from nufox.xul import xulns, htmlns


class Window(Widget):
    """Window."""

    tag = 'window'
    xmlNamespaces = [xulns, htmlns]

    def __init__(self, **kwargs):
        kwargs.setdefault('onload', 'server.callRemote("live");')
        Widget.__init__(self, **kwargs)

    def title(self):
        """title() -> deferred title of window"""
        return self.getAttr(u'title')

    @defgen
    def setTitle(self, title):
        """setTitle(title) -> deferred title of window."""
        # Set the `title` attribute of the XUL window, and also set
        # the title of the browser window.
        yield wait(DeferredList([
            self.setAttr(u'title', title),
            self.pageCtx.callRemote('setWindowTitle', title),
            ]))
        yield title

    @defgen
    def dimensions(self):
        """dimensions() -> deferred (width, height) of window"""
        yield wait(DeferredList([
            self.getAttr(u'width'),
            self.getAttr(u'height'),
            ]))
        yield tuple(result for success, result in results)

    @defgen
    def setDimensions(self, width=None, height=None):
        """setDimensions(width, height) -> deferred (width, height) of
        window"""
        if not width or not height:
            # Get existing dimensions.
            dimensions = wait(self.dimensions())
            yield dimensions
            dimensions = dimensions.getResult()
            # Update new dimensions as necessary.
            curWidth, curHeight = dimensions
            width = width or curWidth
            height = height or curHeight
        # Set the height and width of the XUL window, and resize the
        # browser window.
        yield wait(DeferredList([
            self.setAttr(u'width', width),
            self.setAttr(u'height', height),
            self.pageCtx.callRemote(u'resizeWindow', width, height),
            ]))
        yield (width, height)

