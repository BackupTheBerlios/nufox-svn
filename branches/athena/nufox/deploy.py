from twisted.internet import defer
from nevow import rend, appserver
from nufox import xul

class ResourceDispatcher(rend.Page):
    addSlash=True
    def getRoot(self, context):
        """override me to return the resource you want dispatched"""
    def renderHTTP(self, context):
        d = defer.maybeDeferred(self.getRoot, context)
        d.addCallback(self._delegate, "renderHTTP", context)
        return d
    def locateChild(self, context, segments):
        d = defer.maybeDeferred(self.getRoot, context)
        d.addCallback(self._delegate, "locateChild", context, segments)
        return d
    def _delegate(self, root, funcname, *args):
        return getattr(root, funcname)(*args)


class LivePageFactoryAsRootDispatcher(ResourceDispatcher):

    def __init__(self, factory):
        ResourceDispatcher.__init__(self)
        self.factory = factory

    def getRoot(self, context):
        return self.factory.clientFactory(context)


def NufoxSite(XULRootPage):
    return appserver.NevowSite(LivePageFactoryAsRootDispatcher(
        xul.XULLivePageFactory(XULRootPage)))

def NufoxServer(serviceName, port, XULRootPage, **kwargs):
    application = service.Application(serviceName)
    ws = internet.TCPServer(port, NufoxSite(XULRootPage), **kwargs)
    ws.setServiceParent(application)
    return application
