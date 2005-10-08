from twisted.internet import defer
from twisted.python.util import sibpath
from nevow import url, loaders, inevow, athena, static, tags as T, flat
import xmlstan

#these are XUL elements that should not have an end tag, add to the
#list as you find more:
singletons = ('key',)

#XML Namespaces
htmlns = xmlstan.TagNamespace('html', 'http://www.w3.org/1999/xhtml')
xulns = xmlstan.PrimaryNamespace('xul',
    'http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul',
    singletons=singletons)

class XULPage(athena.LivePage):
    """I am a nevow resource that renders XUL. You should set a xul widget to
    self.window in your subclass' setup method. js and css attributes can be
    used to add inline javascript or css to your page.
    jsIncludes and cssIncludes are lists of urls to javascript and css files
    respectivly, and if set will be included as links in the output. """

    js = None
    css = None
    jsIncludes = []
    cssIncludes = []
    addSlash = True
    constrainDimensions = False
    child_javascript = static.File(sibpath(__file__, 'javascript'))
    charset = "UTF-8"
    glueInstalled = False

    def beforeRender(self, ctx):
        self._initWidgets(self.window)

    def goingLive(self, ctx):
        #some hacks for in-browser apps
        if 'title' in self.window.kwargs:
            self.window.setTitle(self.window.kwargs['title'])

        if self.constrainDimensions:
            self.window.setDimensions(self.window.kwargs.get('height'),
                                      self.window.kwargs.get('width'))

    def _initWidgets(self, widget):
        """Recurse through the widgets children and set self as pageCtx, also
        take any handlers they have defined and assign them to self.handlers
        for use later in locateHandler."""
        if not hasattr(self, 'handlers'):
            self.handlers = {}
        if isinstance(widget, GenericWidget) and widget.pageCtx is None:
            #assign self as pageCtx to the widget
            widget.pageCtx = self
            #add all the handlers from the widget to our list of handlers
            self.handlers[str(widget.id)] = widget.handlers
            for child in widget.children:
                self._initWidgets(child)
        else:
            print "ALREADY BEEN HERE!", widget

    def locateMethod(self, ctx, methodName):
        if methodName.startswith('__'):
            fud, widgetID, event = methodName.split('__')
            return lambda ctx, methodName, *args: self.handlers[widgetID][event][0](*args)
        return athena.LivePage.locateMethod(self, ctx, methodName)

    def renderHTTP(self, ctx):

        self.setup()

        #ensure that we are delivered with the correct content type header
        inevow.IRequest(ctx).setHeader("Content-Type",
            "application/vnd.mozilla.xul+xml; charset=%s" % (self.charset,))

        #Do something a bit magical.. glue css/js stuff into the window before
        #any other widgets so they get read first.
        if self.css is not None:
            self.window.children.insert(0,
                htmlns.style(type="text/css")[self.css])
        self.css = None

        for css in self.cssIncludes:
            self.window.children.insert(0,
                htmlns.style(type="text/css", src=css))
        self.cssIncludes = []

        if self.js is not None:
            self.window.children.insert(0,
                htmlns.script(type="text/javascript")[self.js])
        self.js = None

        for js in self.jsIncludes:
            self.window.children.insert(0,
                htmlns.script(type="text/javascript", src=js))
        self.jsIncludes = []

        #We want to have javascript included in this order:
        #   preLiveglue.js
        #   liveglue.js
        #   postLiveglue.ps

        if not self.glueInstalled:

            self.window.children.insert(0, htmlns.script(
                type="text/javascript", src=url.here.child(
                    'javascript').child('postLiveglue.js')))

            self.window.children.insert(0, T.invisible(
                render=T.directive('liveglue')))

            self.window.children.insert(0, htmlns.script(
                type="text/javascript", src=url.here.child(
                    'javascript').child('preLiveglue.js')))

            self.glueInstalled = True

        #.. end magical

        #make sure our XUL tree is loaded and our correct doc type is set
        self.docFactory = loaders.stan([
            T.xml("""<?xml version="1.0"?><?xml-stylesheet href="chrome://global/skin/" type="text/css"?>"""),
            self.window])
        #return our XUL
        return athena.LivePage.renderHTTP(self, ctx)



class GenericWidget(object):
    """I am the base class for all XUL elements."""

    def __init__(self, ID=None):
        self.children = []
        self.handlers = {}
        self.pageCtx = None
        if ID is None:
            self.id = abs(id(self))
        else:
            self.id = ID
        self.alive = False

    def append(self, *widgets):
        """Use append when appending to widgets that are not live, returns
        self, this is mostly useful in self.setup() and in methods that create
        a sub-tree of widgets to return for appending to a live widget."""
        if self.alive:
            raise RuntimeError("Use liveAppend to append to a live widget.")
        for widget in widgets:
            self.children.append(widget)
            if self.pageCtx is not None:
                self.pageCtx._initWidgets(widget)
        return self

    def liveAppend(self, *widgets):
        """Use liveAppend when appending to widgets that are already live (on
        the client). Returns a deferred. This will also work for non-live
        widget appends, but will still return a deferred, for a more
        convenient append api for non-live widgets, see append."""
        if not self.alive:
            return defer.succeed(self.append(*widgets))
        else:
            newNodes = []
            def marshal(parent):
                for child in parent.children:
                    if child.alive:
                        continue
                    child.alive = True
                    newNodes.append((parent.id, child.tag, child.args))
                    marshal(child)
            marshal(self)
            d = self.pageCtx.callRemote('appendNodes', newNodes)
            d.addCallback(lambda r: self)
            return d

    def __getitem__(self, *widgets):
        """A convenience method for building trees of widgets like you
        would stan tags"""
        return self.append(*widgets)

    def remove(self, *widgets):
        """Remove some widgets from the client under this one. returns a 
        deferred."""
        for widget in widgets:
            self.children.remove(widget)
            if self.alive:
                return self.pageCtx.callRemote('removeNodes',
                                               [w.id for w in widgets])
            return defer.succeed(None)

    def clear(self):
        """Remove all widgets under this one."""
        self.remove(*self.children)

    def getChild(self, id):
        matches = [child for child in self.children
            if hasattr(child, 'id') and str(child.id) == str(id)]
        return len(matches) and matches[0] or None

    def rend(self, context):
        self.alive = True
        return self.getTag()[self.children]

    def setAttr(self, attr, value):
        return self.pageCtx.callRemote('setAttr', self.id,
                                       attr.decode('ascii'), value)

    def callMethod(self, method, *args):
        """call method with args on this node."""
        return self.pageCtx.callRemote('callMethod', self.id, method, args)

    def getAttr(self, attr):
        """Get the value of a remote attribute."""
        return self.pageCtx.callRemote("getAttr", self.id, attr.decode('ascii'))

    def requestAttr(self, attr):
        """You can pass me as an extra argument to addHandler to get the result
        of this attribute lookup passed to your handler."""
        return "a__%s__%s" % (self.id, attr)

    def addHandler(self, event, handler, *args):
        arguments = ""
        if len(args) != 0:
            arguments = ", " + ",".join(map((lambda s: "'%s'" % (s,)),args))
        call = "rCall(this, '%s'%s)" % (event, arguments)
        self.handlers[event] = (handler, call)


flat.registerFlattener(lambda orig, ctx: orig.rend(ctx), GenericWidget)

### WIDGETS BE HERE, ARGH! ###

class Window(GenericWidget):

    def __init__(self, *xmlNameSpaces, **kwargs):
        if kwargs.has_key('id'):
            GenericWidget.__init__(self, kwargs['id'])
        else:
            GenericWidget.__init__(self)
        kwargs.update({'id' : self.id})
        self.kwargs = kwargs
        self.xmlNameSpaces = xmlNameSpaces

    def render_liveglue(self, ctx, data):
        return self.pageCtx.render_liveglue(ctx, data)

    def setTitle(self, title):
        self.setAttr('title', title)
#        self.pageCtx.client.send(
#            livepage.js('document.title = \'%s\';' % title))

    def setDimensions(self, width=None, height=None):
        width = width or self.kwargs.get('width')
        height = height or self.kwargs.get('height')

        self.setAttr('height', height)
        self.setAttr('width', width)
#       self.pageCtx.client.send(
#            livepage.js('window.resizeTo(%s,%s);' % (height, width)))

    def getTag(self):
        self.kwargs.update(dict([(k,v[1]) for k,v in self.handlers.items()]))
        return xulns.window(xulns, htmlns, *self.xmlNameSpaces, **self.kwargs)

### DYNAMICALLY GENERATED WIDGETS BE HERE, DOUBLE ARGH!! ###

class XULWidgetTemplate(GenericWidget):
    def __init__(self, **kwargs):
        if kwargs.has_key('id'):
            GenericWidget.__init__(self, kwargs['id'])
        else:
            GenericWidget.__init__(self)
        kwargs.update({'id':self.id})
        self.kwargs = kwargs

    def getTag(self):
        self.kwargs.update(dict([(k,v[1]) for k,v in self.handlers.items()]))
        return getattr(xulns, self.tag)(**self.kwargs)

#for each widget that has not yet been defined from our big list of XUL tags,
#create a widget class that behaves like a good widget should and does nothing
#fancy.
bigListOXulTags = ['Action', 'ArrowScrollBox', 'BBox', 'Binding', 'Bindings',
    'Box', 'Broadcaster', 'BroadcasterSet', 'Button', 'Browser', 'Checkbox',
    'Caption', 'ColorPicker', 'Column', 'Columns', 'CommandSet', 'Command',
    'Conditions', 'Content', 'Deck', 'Description', 'Dialog', 'DialogHeader',
    'Editor', 'Grid', 'Grippy', 'GroupBox', 'HBox', 'IFrame', 'Image', 'Key',
    'KeySet', 'Label', 'ListBox', 'ListCell', 'ListCol', 'ListCols',
    'ListHead', 'ListHeader', 'ListItem', 'Member', 'Menu', 'MenuBar',
    'MenuItem', 'MenuList', 'MenuPopup', 'MenuSeparator', 'Observes',
    'Overlay', 'Page', 'Popup', 'PopupSet', 'ProgressMeter', 'Radio',
    'RadioGroup', 'Resizer', 'Row', 'Rows', 'Rule', 'Script', 'Scrollbar',
    'Scrollbox', 'Separator', 'Spacer', 'Splitter', 'Stack', 'StatusBar',
    'StatusBarPanel', 'StringBundle', 'StringBundleSet', 'Tab', 'TabBrowser',
    'TabBox', 'TabPanel', 'TabPanels', 'Tabs', 'Template', 'TextNode',
    'TextBox', 'TitleBar', 'ToolBar', 'ToolBarButton', 'ToolBarGrippy',
    'ToolBarItem', 'ToolBarPalette', 'ToolBarSeparator', 'ToolbarSet',
    'ToolBarSpacer', 'ToolBarSpring', 'ToolBox', 'ToolTip', 'Tree', 'TreeCell',
    'TreeChildren', 'TreeCol', 'TreeCols', 'TreeItem', 'TreeRow',
    'TreeSeparator','Triple', 'VBox', 'Window', 'Wizard', 'wizardPage']

g = globals()

for t in bigListOXulTags:
    if t not in g.keys():
        g[t] = type(t, (XULWidgetTemplate,), {'tag' : t.lower()})
