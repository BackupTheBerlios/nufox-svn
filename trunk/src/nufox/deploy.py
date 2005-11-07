"""Nufox deployment helpers."""

import os

from nevow import rend, appserver

from twisted.application import internet, service
from twisted.internet import defer, reactor, utils

from nufox import xul


class ResourceDispatcher(rend.Page):
    
    addSlash = True
    
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


# --------------------------------------------------------------------
# Desktop app support.


class DesktopPageFactory(xul.XULLivePageFactory):
    """XULLivePageFactory that stops the reactor after its last child
    factory ceases to exist."""
    
    firstPageRequested = False

    def addClient(self, client):
        # Keep track of the fact that at least one client has
        # connected.
        self.firstPageRequested = True
        return xul.XULLivePageFactory.addClient(self, client)

    def removeClient(self, clientID):
        xul.XULLivePageFactory.removeClient(self, clientID)
        if self.firstPageRequested and not self.clients:
            # Last client has disconnected; stop reactor at next
            # iteration.
            from twisted.internet import reactor
            reactor.callLater(0, reactor.stop)


def NufoxDesktopApp(XULRootPage, port=None, interface=None, firefoxArgs=None):
    """Use this to run a server with a single client on the same machine."""
    if not interface:
        interface = '127.0.0.1'
    if not port:
        port = 8090
    # Start Firefox as a child process.
    def start():
        args = ['-chrome', 'http://127.0.0.1:8090']
        if firefoxArgs:
            args.extend(firefoxArgs)
        if os.name == 'nt':
            executable = 'C:/Program Files/Mozilla Firefox/firefox.exe'
        else:
            executable = '/usr/bin/firefox'
        utils.getProcessOutput(executable, args, os.environ)
    reactor.callLater(0, start)
    # Create the application.  Because Firefox may return immediately
    # if a Firefox process is already running, don't worry about when
    # Firefox exits.
    application = service.Application('NufoxDesktopApp')
    site = appserver.NevowSite(LivePageFactoryAsRootDispatcher(
        DesktopPageFactory(XULRootPage)))
    ws = internet.TCPServer(port, site, interface=interface)
    ws.setServiceParent(application)
    return application
