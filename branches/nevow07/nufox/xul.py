"""Nufox standard XUL classes and widgets."""

import os

from twisted.internet import defer
from twisted.python.util import sibpath

from nevow import athena, url, loaders, inevow, static, tags as T, flat

from nufox.defer import defgen, wait
from nufox import xmlstan

# These are XUL elements that should not have an end tag. Please add
# to the list as you find more:
singletons = ('key',)


# XML Namespaces.
htmlns = xmlstan.TagNamespace('html', 'http://www.w3.org/1999/xhtml')
xulns = xmlstan.PrimaryNamespace('xul',
    'http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul',
    singletons=singletons)


def requestFunction(func, *args):
    """Get the result of a global function passed to a handler.

    Pass as an extra argument to addHandler calls.
    """
    return ["_f", func, list(args)]


class XULLivePageFactory(athena.LivePageFactory):
    """LivePageFactory that stores child factory instances."""

    noisy = False
    
    def __init__(self, *args, **kwargs):
        self.childFactories = {}
        athena.LivePageFactory.__init__(self, *args, **kwargs)

    def getChildFactory(self, name, LivePageClass,
                        FactoryClass=athena.LivePageFactory, *args, **kwargs):
        if not name in self.childFactories:
            self.childFactories[name] = FactoryClass(LivePageClass,
                                                     *args, **kwargs)
        return self.childFactories[name]


class XULPage(athena.LivePage):
    """Nevow resource that renders XUL.

    Important methods:

    - `setup(self)`: Create this method in your subclass, and have it
      set `self.window` to the main XUL widget for your XULPage.

    Important attributes:

    - `css`: Optional - source of stylesheet to include in the page
      after loading glue scripts.

    - `cssIncludes`: Optional - list of stylesheet URLs to link to in
      the page after loading glue scripts.

    - `js`: Optional - source of JavaScript to include in the page
      after loading glue scripts.

    - `jsIncludes`: Optional - list of JavaScript URLs to link to in
      the page after loading glue scripts.
    """

    js = None
    css = None
    jsIncludes = []
    cssIncludes = []
    globalJsIncludes = []
    widgetJsIncludes = []
    addSlash = True
    constrainDimensions = False
    child_javascript = static.File(sibpath(__file__, 'javascript'))
    child_js_composite = static.File(os.path.join(
        sibpath(__file__, 'composite'), 'javascript'))
    child_js_widget = static.File(os.path.join(
        sibpath(__file__, 'widget'), 'javascript'))
    charset = "UTF-8"
    glueInstalled = False

    liveChildren = {}

    # Use a saner default idle timeout of one hour.
    TRANSPORT_IDLE_TIMEOUT = 60 * 60

    def beforeRender(self, ctx):
        self._initWidgets(self.window)

    def goingLive(self, ctx):
        athena.LivePage.goingLive(self, ctx)
        # Some hacks for in-browser apps.
        if 'title' in self.window.kwargs:
            self.window.setTitle(self.window.kwargs['title'])
        if self.constrainDimensions:
            self.window.setDimensions(self.window.kwargs.get('height'),
                                      self.window.kwargs.get('width'))
        # Perform post-livepage stuff.
        self.setupLive()
        self._initWidgets(self.window, 'setupLive')

    def setup(self):
        """Set up the page.  By default, does nothing.  Override in
        subclasses."""

    def setupLive(self):
        """Set up the page after it is at the client.  Override in
        subclasses."""

    def _initWidgets(self, widget, methodName=None, parent=None):
        """Set `pageCtx` of `widget` and its children to this page,
        and keep track of them for the purposes of handlers and remote
        method invocation.

        If `methodName` is specified, it will call an optional method
        of that name on each widget instead of the default behavior.
        """
        if not methodName:
            # Create self.widgets if necessary.
            id_widget = self.id_widget = getattr(self, 'id_widget', {})
            # Process the current widget.
            if isinstance(widget, GenericWidget) and widget.pageCtx is None:
                # Assign this page to the `pageCtx` attribute on the
                # widget.
                widget.pageCtx = self
                # Let the widget know its place in the hierarchy.
                widget.parent = parent
                # Keep track of widget ID to widget mappings, for handlers
                # and remote method invocations.
                id_widget[unicode(widget.id)] = widget
                for child in widget.children:
                    self._initWidgets(child, parent=widget)
        else:
            # Call an optional method on each widget.
            if isinstance(widget, GenericWidget):
                from twisted.internet import reactor
                method = getattr(widget, methodName, None)
                if method is not None:
                    reactor.callLater(0, method)
                for child in widget.children:
                    self._initWidgets(child, methodName)

    def locateMethod(self, ctx, methodName):
        if methodName.startswith('__'):
            fud, widgetID, event = methodName.split('__')
            return lambda ctx, methodName, *args: (
                self.id_widget[widgetID].handlers[event][0](*args))
        return athena.LivePage.locateMethod(self, ctx, methodName)

    def remote_widgetMethod(self, widgetId, methodName, *args):
        widget = self.id_widget[unicode(widgetId)]
        def methodNotFound(*args):
            raise NameError(
                'Method %s on %r not found.' % (methodName, widget))
        return getattr(
            self.id_widget[unicode(widgetId)],
            'remote_%s' % methodName,
            notfound,
            )(*args)

    def renderHTTP(self, ctx):
        # Call user-defined setup, so self.window becomes available.
        self.setup()
        # Ensure that we are delivered with the correct content type
        # header.
        inevow.IRequest(ctx).setHeader(
            "Content-Type",
            "application/vnd.mozilla.xul+xml; charset=%s" % (self.charset,))
        # Apply user-defined and required glue.
        self.applyAllGlue()
        # Make sure our XUL tree is loaded and our correct doc type is
        # set.
        self.docFactory = loaders.stan([
            T.xml('<?xml version="1.0"?>'
                  '<?xml-stylesheet href="chrome://global/skin/" '
                  'type="text/css"?>'),
            self.window,
            ])
        # Return our XUL.
        return athena.LivePage.renderHTTP(self, ctx)

    def childFactory(self, ctx, name):
        if name in self.liveChildren:
            return self.factory.getChildFactory(
                name, self.liveChildren[name],
                XULLivePageFactory).clientFactory(ctx)
        else:
            return athena.LivePage.childFactory(self, ctx, name)

    def applyAllGlue(self):
        """Install all glue scripts in the proper order."""
        if not self.glueInstalled:
            # Apply user-supplied glue.  Glue is applied in reverse
            # order.
            self.applyCssCode(self.css)
            for URL in self.cssIncludes:
                self.applyCssUrl(URL)
            self.applyJsCode(self.js)
            for URL in self.jsIncludes:
                self.applyJsUrl(URL)
            # Apply globally-registered glue that resulted from
            # importing a module from the nufox.composite package.
            for filename in self.globalJsIncludes:
                self.applyJsUrl(
                    url.here.child('js_composite').child(filename))
            # Apply globally-registered glue that resulted from
            # importing a module from the nufox.widget package.
            for filename in self.widgetJsIncludes:
                self.applyJsUrl(
                    url.here.child('js_widget').child(filename))
            # Required glue is at the top of the chain.
            self.applyJsUrl(
                url.here.child('javascript').child('postLiveglue.js'))
            self.applyLiveglue()
            self.applyJsUrl(
                url.here.child('javascript').child('preLiveglue.js'))
            # Done.
            self.glueInstalled = True

    def applyCssCode(self, code):
        """Include CSS code during glue loading."""
        if code:
            self.window.children.insert(0, htmlns.style(
                type="text/css")[code])

    def applyCssUrl(self, URL):
        """Link to a CSS URL during glue loading."""
        self.window.children.insert(0, htmlns.script(
            type='text/css', src=URL))

    def applyLiveglue(self):
        self.window.children.insert(0, T.invisible(
            render=T.directive('liveglue')))

    def applyJsCode(self, code):
        """Include JavaScript code during glue loading."""
        if code:
            self.window.children.insert(0, htmlns.script(
                type="text/javascript")[code])

    def applyJsUrl(self, URL):
        """Link to a JavaScript URL during glue loading."""
        self.window.children.insert(0, htmlns.script(
            type='text/javascript', src=URL))


class GenericWidget(object):
    """I am the base class for all XUL elements."""

    namespace = xulns

    def __init__(self, ID=None):
        self.parent = None
        self.children = []
        self.handlers = {}
        self.pageCtx = None
        if ID is None:
            id_self = id(self)
            # Ensure uniqueness even when negative.
            ID = unicode(abs(id_self))
            if id_self < 0:
                ID += u'n'
            self.id = ID
        else:
            self.id = unicode(ID)
        self.alive = False

    def append(self, *widgets):
        """Use append when appending to widgets that are not live,
        returns self, this is mostly useful in self.setup() and in
        methods that create a sub-tree of widgets to return for
        appending to a live widget."""
        if self.alive:
            raise RuntimeError("Use liveAppend to append to a live widget.")
        return self._append(*widgets)

    def _append(self, *widgets):
        for widget in widgets:
            self.children.append(widget)
            if self.pageCtx is not None:
                self.pageCtx._initWidgets(widget, parent=self)
        return self

    def adopt(self, node):
        """Make `node` a child of this widget, and return `node`."""
        self.append(node)
        return node

    def close(self):
        """Close this widget.

        Typically, this means removing the widget from its parent,
        although specific widgets may provide alternative behaviors.
        """
        return self.parent.remove(self)

    def insert(self, before, *widgets):
        if self.alive:
            raise RuntimeError("Use liveInsert to insert to a live widget.")
        return self._insert(before, *widgets)

    def _insert(self, before, *widgets):
        idx = self.children.index(before)
        for widget in widgets:
            self.children.insert(idx, widget)
            if self.pageCtx is not None:
                self.pageCtx._initWidgets(widget, parent=self)
            idx += 1
        return self

    def liveAppend(self, *widgets):
        """Use liveAppend when appending to widgets that are already
        live (on the client). Returns a deferred. This will also work
        for non-live widget appends, but will still return a deferred,
        for a more convenient append api for non-live widgets, see
        append."""
        if not self.alive:
            return defer.succeed(self.append(*widgets))
        else:
            self._append(*widgets)
            newNodes = []
            def marshal(parent):
                for child in parent.children:
                    if getattr(child,'alive',False):
                        continue
                    if isinstance(child, unicode):
                        newNodes.append((parent.id, child))
                    else:
                        child.alive = True
                        if isinstance(child, (xmlstan.NSTag, xmlstan.Tag)):
                            pass
                            #XXX FIXME this is BROKEN and needs fixing
                            #raise NotImplementedError(
                            #    "liveAppend anything but XUL "
                            #    "widgets is broken! %r" % child )
                            #newNodes.append(
                            #    (parent.id, child.tagName, child.attributes))
                            #marshal(child)
                        else:
                            tag = child.tag.decode('ascii')
                            if child.namespace is self.namespace:
                                newNodes.append((
                                    parent.id,
                                    tag,
                                    child.kwargs,
                                    ))
                            else:
                                newNodes.append((
                                    parent.id,
                                    child.namespace.uri.decode('ascii'),
                                    tag,
                                    child.kwargs,
                                    ))
                            marshal(child)
            marshal(self)
            d = self.callGlobal('appendNodes', newNodes)
            def initNodes(result):
                _initWidgets = self.pageCtx._initWidgets
                for w in widgets:
                    _initWidgets(w, 'setupLive')
                return self
            d.addCallback(initNodes)
            return d

    def liveInsert(self, before, *widgets):
        if not self.alive:
            return defer.succeed(self.insert(before, *widgets))
        else:
            beforeId = before.id
            self._insert(before, *widgets)
            newNodes = []
            def marshal(parent):
                for child in parent.children:
                    if getattr(child, 'alive', False):
                        continue
                    child.alive = True
                    if isinstance(child, (xmlstan.NSTag, xmlstan.Tag)):
                        # XXX: fixme
                        pass
                    else:
                        newNodes.append((
                            parent.id,
                            before.id,
                            child.tag.decode('ascii'),
                            child.kwargs))
                        marshal(child)
            marshal(self)
            d = self.callGlobal('insertNodes', newNodes)
            def returnSelf(result):
                return self
            d.addCallback(returnSelf)
            return d

    def __getitem__(self, *widgets):
        """A convenience method for building trees of widgets like you
        would stan tags"""
        return self.append(*widgets)

    def remove(self, *widgets):
        """Remove some widgets from the client under this one. returns
        a deferred."""
        for widget in widgets:
            self.children.remove(widget)
        if self.alive:
            return self.callGlobal('removeNodes', self.id,
                                   [w.id for w in widgets])
        return defer.succeed(None)

    def clear(self):
        """Remove all widgets under this one."""
        return self.remove(*self.children)

    def getChild(self, id):
        matches = [child for child in self.children
            if hasattr(child, 'id') and unicode(child.id) == unicode(id)]
        return len(matches) and matches[0] or None

    def rend(self, context):
        self.alive = True
        return self.getTag()[self.children]

    def callMethod(self, method, *args):
        """call method with args on this node."""
        return self.callGlobal(
            'callMethod', self.id, unicode(method, 'ascii'), args)

    @property
    def callGlobal(self):
        return self.pageCtx.callRemote

    @defgen
    def get(self, attr, default=u''):
        """Get the value of a remote attribute."""
        if not self.alive:
            yield self.kwargs.get(attr, default)
        else:
            value = wait(self.callGlobal(
                'getAttr', self.id, attr.decode('ascii')))
            yield value
            value = value.getResult()
            yield value[0][0]
    getAttr = get # Backwards compatibility.

    def set(self, attr, value):
        """Set the value of a remote attribute."""
        if not self.alive:
            self.kwargs[attr] = value
            return defer.succeed(None)
        else:
            return self.callGlobal(
                'setAttr', self.id, attr.decode('ascii'), value)
    setAttr = set # Backwards compatibility.

    def requestAttr(self, attr):
        """You can pass me as an extra argument to addHandler to get the result
        of this attribute lookup passed to your handler."""
        return ["_a", self.id, attr]

    def requestMethod(self, method, *args):
        """You can pass me as an extra argument to addHandler to get the result
        of this method passed to your handler."""
        return ["_m", self.id, method, list(args)]

    def addHandler(self, event, handler, *args):
        args = [u"'%s'" % event] + [repr(a) for a in args]
        call = u'rCall(this, %s)' % ', '.join(args)
        self.handlers[event] = (handler, call)
        self.kwargs[event] = call
        return self

flat.registerFlattener(lambda orig, ctx: orig.rend(ctx), GenericWidget)


# --------------------------------------------------------------------


class Window(GenericWidget):

    def __init__(self, *xmlNameSpaces, **kwargs):
        if kwargs.has_key('id'):
            GenericWidget.__init__(self, kwargs['id'])
        else:
            GenericWidget.__init__(self)
        kwargs.update({'id' : self.id})
        kwargs.setdefault('onload', u'server.callRemote("live");')
        self.kwargs = kwargs
        self.xmlNameSpaces = xmlNameSpaces

    def render_liveglue(self, ctx, data):
        return self.pageCtx.render_liveglue(ctx, data)

    def setTitle(self, title):
        self.setAttr('title', title)
#        self.pageCtx.client.send(
#            livepage.js('document.title = \'%s\';' % title))
        self.callGlobal('setWindowTitle', title)
        
    def setDimensions(self, width=None, height=None):
        width = width or self.kwargs.get('width')
        height = height or self.kwargs.get('height')

        self.setAttr(u'height', height)
        self.setAttr(u'width', width)
#       self.pageCtx.client.send(
#            livepage.js('window.resizeTo(%s,%s);' % (height, width)))
        self.callGlobal('resizeWindow', width, height)

    def getTag(self):
        return xulns.window(xulns, htmlns, *self.xmlNameSpaces, **self.kwargs)


# --------------------------------------------------------------------
# Dynamically generated widgets.

class XULWidgetTemplate(GenericWidget):

    def __init__(self, **kwargs):
        if kwargs.has_key('id'):
            GenericWidget.__init__(self, kwargs['id'])
        else:
            GenericWidget.__init__(self)
        kwargs.update({'id':self.id})
        self.kwargs = kwargs

    def getTag(self):
        return getattr(xulns, self.tag)(**self.kwargs)


# For each widget that has not yet been defined from our big list of
# XUL tags, create a widget class that behaves like a good widget
# should and does nothing fancy.
bigListOXulTags = [
    'Action', 'ArrowScrollBox', 'BBox', 'Binding',
    'Bindings', 'Box', 'Broadcaster', 'BroadcasterSet', 'Button',
    'Browser', 'Checkbox', 'Caption', 'ColorPicker', 'Column', 'Columns',
    'CommandSet', 'Command', 'Conditions', 'Content', 'Deck',
    'Description', 'Dialog', 'DialogHeader', 'Editor', 'Grid', 'Grippy',
    'GroupBox', 'HBox', 'IFrame', 'Image', 'Key', 'KeySet', 'Label',
    'ListBox', 'ListCell', 'ListCol', 'ListCols', 'ListHead',
    'ListHeader', 'ListItem', 'Member', 'Menu', 'MenuBar', 'MenuItem',
    'MenuList', 'MenuPopup', 'MenuSeparator', 'Observes', 'Overlay',
    'Page', 'Popup', 'PopupSet', 'ProgressMeter', 'Radio', 'RadioGroup',
    'Resizer', 'Row', 'Rows', 'Rule', 'Script', 'Scrollbar', 'Scrollbox',
    'Separator', 'Spacer', 'Splitter', 'Stack', 'StatusBar',
    'StatusBarPanel', 'StringBundle', 'StringBundleSet', 'Tab',
    'TabBrowser', 'TabBox', 'TabPanel', 'TabPanels', 'Tabs', 'Template',
    'TextNode', 'TextBox', 'TitleBar', 'ToolBar', 'ToolBarButton',
    'ToolBarGrippy', 'ToolBarItem', 'ToolBarPalette', 'ToolBarSeparator',
    'ToolbarSet', 'ToolBarSpacer', 'ToolBarSpring', 'ToolBox', 'ToolTip',
    'Tree', 'TreeCell', 'TreeChildren', 'TreeCol', 'TreeCols', 'TreeItem',
    'TreeRow', 'TreeSeparator','Triple', 'VBox', 'Window', 'Wizard',
    'WizardPage',
    ]

g = globals()

for t in bigListOXulTags:
    if t not in g.keys():
        g[t] = type(t, (XULWidgetTemplate,), {'tag' : t.lower()})

