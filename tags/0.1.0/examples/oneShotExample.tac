import os
from twisted.python import reflect, log, util
from twisted.internet import utils as tiutils
from nufox import xul

example = reflect.namedAny('%s.example' % os.environ['EXAMPLE'])

from twisted.internet import defer
from nevow import rend, athena

"""hoping this might be allowed into nevow.rend"""
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


"""then this could go into nevow.athena"""
class LivePageFactoryAsRootDispatcher(ResourceDispatcher):
    def __init__(self, factory):
        ResourceDispatcher.__init__(self)
        self.factory = factory
    def getRoot(self, context):
        return self.factory.clientFactory(context)


from twisted.application import internet, service
from nevow import appserver

application = service.Application('xulstan')
webServer = internet.TCPServer(8080, appserver.NevowSite(
    LivePageFactoryAsRootDispatcher(athena.LivePageFactory(example))
    ), interface='127.0.0.1')
webServer.setServiceParent(application)
