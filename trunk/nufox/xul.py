import weakref
from twisted.internet import defer
from nevow import rend, loaders, url, inevow, livepage, tags as T
import xmlstan

htmlns = xmlstan.TagNamespace('html', 'http://www.w3.org/1999/xhtml')
xulns = xmlstan.PrimaryNamespace('xul', 
    'http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul',
    singletons=('key',))

class XULPage(livepage.LivePage):
    """I am a nevow resource that renders XUL."""

    #a string of javascript which will be included at the start of the page.
    js = None 
    #a list of .js files which will be included.
    jsIncludes = None 
    
    def goingLive(self, ctx, client):
        self.client = client
        self._findHandlers(self.window) 

    def _findHandlers(self, widget):
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
                self._findHandlers(child)
        else:
            print "ALREADY BEEN HERE!", widget

    def locateHandler(self, ctx, path, name):
        #lookup our handler based on the returning widget id and name.
        print "LOCATEHANDLER: ", self.handlers.keys()
        return (lambda cli, event, id, *extras: 
            self.handlers[id][event][0](*extras))
        
    def renderHTTP(self, ctx):
        #ensure that we are delivered with the correct content type header
        inevow.IRequest(ctx).setHeader("Content-Type", 
            "application/vnd.mozilla.xul+xml; charset=UTF-8")
        
        #Do something a bit magical.. glue our js stuff into the window before
        #any other widgets so they get read first.
        if self.js is not None:
            self.window.children.insert(0,
                T.script(type="application/x-javascript")[self.js])
        if self.jsIncludes is not None:
            [self.window.children.insert(0,
                T.script(type="application/x-javascript", src=js)) 
                for js in self.jsIncludes or []]
        #.. end magical
       
        #make sure our XUL tree is loaded and our correct doc type is set
        self.docFactory = loaders.stan([
            T.xml("""<?xml version="1.0"?><?xml-stylesheet href="chrome://global/skin/" type="text/css"?>"""),
            self.window])
        #return our XUL
        return livepage.LivePage.renderHTTP(self, ctx)

  
    
class GenericWidget(rend.Fragment):
    
    def __init__(self, ID=None):
        self.children = []
        self.handlers = {}
        self.pageCtx = None

        if ID is None:
            self.id = id(self)
        else:
            self.id = ID
            
    def append(self, *widgets):
        for widget in widgets:
            self.children.append(widget)
            if self.pageCtx is not None:
                self.pageCtx._getWidgetRefs(widget)
        return self

    def getDocFactory(self):
        return loaders.stan(self.getTag()[self.children])
    
    docFactory = property(getDocFactory)
   
    def setAttr(self, cli, attr, value):
        """Set attribute attr to value on this node"""
        node = livepage.get(self.id)
        if isinstance(value, (int, float)):
            s = "%s.%s = %d;"
        else:
            s = "%s.%s = '%s';"
        cli.send(livepage.assign(getattr(node, attr), value))
    
    def callMethod(self, cli, method, *args):
        """call method with args on this node."""
        node = livepage.get(self.id)
        livepage.IClientHandle(cli).send("%s.%s;" % (node, 
            livepage.callJS(method, *args)))
            
    def getAttr(self, cli, attr):
        """Get an attribute from this widget asynchronously, 
        returns a deferred."""
        d = defer.Deferred()
        getter = cli.transient(lambda ctx, r: d.callback(r))
        cli.send(getter(getattr(livepage.get(self.id),attr)))
        return d
   
    def addHandler(self, event, handler, *js):
        """I take an event like 'onclick' or 'oncommand' etc, a callable which
        must take at least a client object as its first param, and then optional
        javascript to be evaluated and returned, as per nevow.livepage JS.
        
        examples:
        
        If the onClick event happens for button, myHandler will be called with
        no arguments:
        
        button.addHandler('onClick', myHandler)
        
        If the onClick event happens for button, myHandler is called with the
        argument 'button'; the actual widget. In this way extra arguments can 
        be passed without the need to send them down the wire.
        
        button.addHandler('onClick', lambda *js: myHandler(button, *js))

        Finally, if the onClick event happens for button, myHandler will be 
        called with the value of another widget

        button.addHandler('onClick', myHandler, livepage.get(widget.id).value)
        """
        self.handlers[event] = (handler, livepage.server.handle(
            handler.__name__, event, self.id, *js)) 
            #send event and widget id to find handler in locateHandler

   
### WIDGETS BE HERE, ARGH! ###

class Window(GenericWidget):

    def __init__(self, **kwargs):
        if kwargs.has_key('id'):
            GenericWidget.__init__(self, kwargs['id'])
        else:
            GenericWidget.__init__(self)
        kwargs.update({'id' : self.id}) 
        self.kwargs = kwargs
    
    #XXX Taken form livepage, this needs re-thinking..
    def render_liveid(self, ctx, data):
        return T.script(type="text/javascript")[
            "var nevow_clientHandleId = '", 
            livepage.IClientHandle(ctx).handleId, "';"]

    def render_liveglue(self, ctx, data):
        return T.script(type="text/javascript", src=url.here.child(
            'nevow_glue.js'))
    # ..end XXX

    def getTag(self):
        self.kwargs.update(dict([(k,v[1]) for k,v in self.handlers.items()]))
        return xulns.window(xulns, htmlns, **self.kwargs)[
            T.invisible(render=T.directive('liveid')),
            T.invisible(render=T.directive('liveglue'))]

     

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
