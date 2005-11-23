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

    def setTitle(self, title):
        """setTitle(title) -> deferred title of window."""
        # Set the `title` attribute of the XUL window, and also set
        # the title of the browser window.
        def returnTitle(result):
            return title
        return DeferredList([
            self.setAttr(u'title', title),
            self.pageCtx.callRemote('setWindowTitle', title),
            ]).addCallback(returnTitle)
        
    def dimensions(self):
        """dimensions() -> deferred (width, height) of window"""
        def toTuple(results):
            return tuple(result for success, result in results)
        return DeferredList([
            self.getAttr(u'width'),
            self.getAttr(u'height'),
            ]).addCallback(toTuple)

    def setDimensions(self, width=None, height=None):
        """setDimensions(width, height) -> deferred (width, height) of
        window"""
        d = Deferred()
        if not width or not height:
            # Get existing dimensions.
            dDimensions = self.dimensions()
            # Update new dimensions as necessary.
            def updateDimensions(dimensions):
                curWidth, curHeight = dimensions
                width = width or curWidth
                height = height or curHeight
                return (width, height)
            d.chainDeferred(dDimensions.addCallback(updateDimensions))
        else:
            # Use new dimensions.
            d.callback((width, height))
        # Set the height and width of the XUL window, and resize the
        # browser window.
        def setXulAttributes(dimensions):
            width, height = dimensions
            def returnDimensions(result):
                return dimensions
            return DeferredList([
                self.setAttr(u'width', width),
                self.setAttr(u'height', height),
                self.pageCtx.callRemote(u'resizeWindow', width, height)
                ]).addCallback(returnDimensions)
        return d.addCallback(setXulAttributes)

