import itertools

from zope.interface import implements

from twisted.internet import defer
from twisted.python import log

from nevow import inevow, rend, url, static, json, util, tags, guard

class LivePageError(Exception):
    """base exception for livepage errors"""

def neverEverCache(request):
    """
    Set headers to indicate that the response to this request should
    never, ever be cached.
    """
    request.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate')
    request.setHeader('Pragma', 'no-cache')

def activeChannel(request):
    """
    Mark this connection as a 'live' channel by setting the
    Connection: close header and flushing all headers immediately.
    """
    request.setHeader("Connection", "close")
    request.write('')

class LivePageTransport(object):
    implements(inevow.IResource)

    def __init__(self, livePage):
        self.livePage = livePage

    def locateChild(self, ctx, segments):
        return rend.NotFound

    def renderHTTP(self, ctx):
        req = inevow.IRequest(ctx)
        try:
            d = self.livePage.addTransport(req)
        except defer.QueueOverflow:
            log.msg("Fast transport-close path")
            d = defer.succeed('')
        args = req.args.get('args', [()])[0]
        if args != ():
            args = json.parse(args)
        kwargs = req.args.get('kw', [{}])[0]
        if kwargs != {}:
            args = json.parse(kwargs)
        method = getattr(self, 'action_' + req.args['action'][0])
        method(ctx, *args, **kwargs)

        return d.addCallback(self._cbRender)

    def _cbRender(self, result):
        log.msg("Sending some output to a transport: %r" % (result,))
        return result

    def _cbCall(self, result, requestId):
        def cb((d, req)):
            d.callback((None, unicode(requestId), u'text/json', result))
        self.livePage.getTransport().addCallback(cb)

    def _ebCall(self, err, method, func):
        log.msg("Dispatching %r to %r failed unexpectedly:" % (method, func))
        log.err(err)
        return err

    def action_call(self, ctx, method, *args, **kw):
        func = self.livePage.locateMethod(ctx, method)
        log.msg("Dispatching %r to %r (args: %r, kwargs: %r)" % (method, func, args, kw))

        requestId = inevow.IRequest(ctx).getHeader('Request-Id')
        if requestId is not None:
            result = defer.maybeDeferred(func, ctx, *args, **kw)
            result.addErrback(self._ebCall, method, func)
            result.addBoth(self._cbCall, requestId)
        else:
            try:
                func(ctx, *args, **kw)
            except:
                log.msg("Unhandled error in event handler:")
                log.err()

    def action_respond(self, ctx, *args, **kw):
        responseId = inevow.IRequest(ctx).getHeader('Response-Id')
        log.msg("Responding to request %r (args: %r, kwargs: %r)" % (responseId, args, kw))
        if responseId is None:
            log.msg("No Response-Id given")
            return

        self.livePage._remoteCalls.pop(responseId).callback((args, kw))

    def action_noop(self, ctx):
        pass


class LivePageFactory:
    noisy = True

    def __init__(self, pageFactory):
        self._pageFactory = pageFactory
        self.clients = {}

    def clientFactory(self, context):
        livepageId = inevow.IRequest(context).getHeader('Livepage-Id')
        if livepageId is not None:
            livepage = self.clients.get(livepageId)
            if livepage is not None:
                # A returning, known client.  Give them their page.
                return livepage
            else:
                # A really old, expired client.  Or maybe an evil
                # hax0r.  Give them a fresh new page and log the
                # occurrence.
                if self.noisy:
                    log.msg("Unknown Livepage-Id: %r" % (livepageId,))
                return self._manufactureClient()
        else:
            # A brand new client.  Give them a brand new page!
            return self._manufactureClient()

    def _manufactureClient(self):
        cl = self._pageFactory()
        cl.factory = self
        return cl

    def addClient(self, client):
        id = self._newClientID()
        self.clients[id] = client
        if self.noisy:
            log.msg("Rendered new LivePage %r: %r" % (client, id))
        return id

    def _newClientID(self):
        return guard._sessionCookie()

    def getClients(self):
        return self.clients.values()


def liveLoader(PageClass, FactoryClass=LivePageFactory):
    """
    Helper for handling Page creation for LivePage applications.

    Example::

        class Foo(Page):
            child_app = liveLoader(MyLivePage)

    This is an experimental convenience function.  Consider it even less
    stable than the rest of this module.
    """
    fac = FactoryClass(PageClass)
    def liveChild(self, ctx):
        return fac.clientFactory(ctx)
    return liveChild


class LivePage(rend.Page):
    transportFactory = LivePageTransport
    transportLimit = 2
    _rendered = False

    factory = None
    _transportQueue = None
    _requestIDCounter = None
    _remoteCalls = None
    clientID = None

    def renderHTTP(self, ctx):
        assert not self._rendered, "Cannot render a LivePage more than once"
        assert self.factory is not None, "Cannot render a LivePage without a factory"
        self._rendered = True
        self._requestIDCounter = itertools.count().next
        self._transportQueue = defer.DeferredQueue(size=self.transportLimit)
        self._remoteCalls = {}

        self.clientID = self.factory.addClient(self)

        neverEverCache(inevow.IRequest(ctx))
        return rend.Page.renderHTTP(self, ctx)

    def _ebOutput(self, err):
        msg = u"%s: %s" % (err.type.__name__, err.getErrorMessage())
        return 'throw new Error(%s);' % (json.serialize(msg),)

    def addTransport(self, req):
        neverEverCache(req)
        activeChannel(req)

        d = defer.Deferred()
        d.addCallbacks(json.serialize, self._ebOutput)
        self._transportQueue.put((d, req))
        return d

    def getTransport(self):
        return self._transportQueue.get()

    def _cbCallRemote(self, (d, req), methodName, args):
        requestID = u's2c%i' % (self._requestIDCounter(),)
        objectID = 0
        d.callback((requestID, None, (objectID, methodName, tuple(args))))

        resultD = defer.Deferred()
        self._remoteCalls[requestID] = resultD
        return resultD

    def callRemote(self, methodName, *args):
        return self.getTransport().addCallback(self._cbCallRemote, unicode(methodName, 'ascii'), args)

    def render_liveglue(self, ctx):
        return [
            tags.script(type='text/javascript')[tags.raw("""
                var nevow_livepageId = '%s';
            """ % self.clientID)],
            tags.script(type='text/javascript', src=url.here.child("mochikit.js")),
            tags.script(type='text/javascript', src=url.here.child("athena.js")),
        ]

    _javascript = {'mochikit.js': 'MochiKit.js',
                   'athena.js': 'athena.js'}
    def childFactory(self, ctx, name):
        if name in self._javascript:
            return static.File(util.resource_filename('nevow', self._javascript[name]))

    def child_transport(self, ctx):
        assert self._rendered, "Impossible!"
        return self.transportFactory(self)

    def locateMethod(self, ctx, methodName):
        return getattr(self, 'remote_' + methodName)

    def remote_live(self, ctx):
        """
        Framework method invoked by the client when it is first
        loaded.  This simply dispatches to goingLive().
        """
        self.goingLive(ctx)
        self._onDisconnect = defer.Deferred()
        return self._onDisconnect

    def goingLive(self, ctx):
        pass
