from twisted.internet import defer
from nevow import rend, loaders, url, inevow, livepage, tags as T
import xmlstan

xulns = xmlstan.PrimaryNamespace('xul')

class XULPage(livepage.LivePage):
    js = None #a string of js which will be included at the start of the page.
    jsIncludes = None #a list of .js files which will be included.
    
    def goingLive(self, ctx, client):
        self.client = client

    def renderHTTP(self, ctx):
        inevow.IRequest(ctx).setHeader("Content-Type", 
            "application/vnd.mozilla.xul+xml; charset=UTF-8")
           
        #Do something a bit ugly...
        if self.js is not None:
            self.window.children.insert(0,
                T.script(type="application/x-javascript")[self.js])
        if self.jsIncludes is not None:
            [self.window.children.insert(0,
                T.script(type="application/x-javascript", src=js)) 
                for js in self.jsIncludes or []]
        #.. end ugly
        
        self.docFactory = loaders.stan([
            T.xml("""<?xml version="1.0"?><?xml-stylesheet href="chrome://global/skin/" type="text/css"?>"""),
            self.window])

        return livepage.LivePage.renderHTTP(self, ctx)
    
class GenericWidget(rend.Fragment):
    
    def __init__(self, ID=None):
        self.children = []
        self.handlers = {}
        if ID is None:
            self.id = id(self)
        else:
            self.id = ID
            
    def append(self, w):
        self.children.append(w)
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
        livepage.IClientHandle(cli).send("%s.%s;" % (node, livepage.callJS(method, *args)))
    
    def addHandler(self, event, handler, *js):
        self.handlers[event] = livepage.server.handle(handler, *js)

    def getAttr(self, cli, attr):
        d = defer.Deferred()
        getter = cli.transient(lambda ctx, r: d.callback(r))
        cli.send(getter(getattr(livepage.get(self.id),attr)))
        return d


   
# create every tag class at runtime..
class XULWidgetTemplate(GenericWidget):
    
    def __init__(self, **kwargs):
        if kwargs.has_key('id'):
            GenericWidget.__init__(self, kwargs['id'])
        else:
            GenericWidget.__init__(self)
        kwargs.update({'id':self.id})
        self.kwargs = kwargs
    
    
    def getTag(self):
        self.kwargs.update(self.handlers)
        print "HEY HANDLERS", self.handlers
        return getattr(xulns, self.tag)(**self.kwargs)

g = globals()
for t in ['Action', 'ArrowScrollBox', 'BBox', 'Binding', 'Bindings', 'Box', 
'Broadcaster', 'BroadcasterSet', 'Button', 'Browser', 'Checkbox', 'Caption', 
'ColorPicker', 'Column', 'Columns', 'CommandSet', 'Command', 'Conditions', 
'Content', 'Deck', 'Description', 'Dialog', 'DialogHeader', 'Editor', 'Grid', 
'Grippy', 'GroupBox', 'HBox', 'IFrame', 'Image', 'Key', 'KeySet', 'Label', 
'ListBox', 'ListCell', 'ListCol', 'ListCols', 'ListHead', 'ListHeader', 
'ListItem', 'Member', 'Menu', 'MenuBar', 'MenuItem', 'MenuList', 'MenuPopup', 
'MenuSeparator', 'Observes', 'Overlay', 'Page', 'Popup', 'PopupSet', 
'ProgressMeter', 'Radio', 'RadioGroup', 'Resizer', 'Row', 'Rows', 'Rule', 
'Script', 'Scrollbar', 'Scrollbox', 'Separator', 'Spacer', 'Splitter', 
'Stack', 'StatusBar', 'StatusBarPanel', 'StringBundle', 'StringBundleSet', 
'Tab', 'TabBrowser', 'TabBox', 'TabPanel', 'TabPanels', 'Tabs', 'Template', 
'TextNode', 'TextBox', 'TitleBar', 'ToolBar', 'ToolBarButton', 'ToolBarGrippy',
'ToolBarItem', 'ToolBarPalette', 'ToolBarSeparator', 'ToolbarSet', 
'ToolBarSpacer', 'ToolBarSpring', 'ToolBox', 'ToolTip', 'Tree', 'TreeCell', 
'TreeChildren', 'TreeCol', 'TreeCols', 'TreeItem', 'TreeRow', 'TreeSeparator',
'Triple', 'VBox', 'Window', 'Wizard', 'wizardPage']:
    g[t] = type(t, (XULWidgetTemplate,), {'tag' : t.lower()})

#Override any that need special treatment


class Window(GenericWidget):

    def __init__(self, **kwargs):
        if kwargs.has_key('id'):
            GenericWidget.__init__(self, kwargs['id'])
        else:
            GenericWidget.__init__(self)
        kwargs.update({'id' : self.id,
            'xmlns' : 'http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul'})
        self.kwargs = kwargs
       
    #Taken form livepage..
    
    def render_liveid(self, ctx, data):
        return T.script(type="text/javascript")[
            "var nevow_clientHandleId = '", livepage.IClientHandle(ctx).handleId, "';"]

    def render_liveglue(self, ctx, data):
        return T.script(type="text/javascript", src=url.here.child('nevow_glue.js'))


    def getTag(self):
        self.kwargs.update(self.handlers)
        return xulns.window(**self.kwargs)[
            T.invisible(render=T.directive('liveid')),
            T.invisible(render=T.directive('liveglue'))]

