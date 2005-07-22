from nevow import rend, loaders, inevow, tags as T
import xmlstan

x = xmlstan.PrimaryNamespace('xul')

class XULPage(rend.Page):

    def beforeRender(self, ctx):
        inevow.IRequest(ctx).setHeader("Content-Type", 
            "application/vnd.mozilla.xul+xml; charset=UTF-8")
        self.docFactory = loaders.stan([
            T.xml("""<?xml version="1.0"?><?xml-stylesheet href="chrome://global/skin/" type="text/css"?>"""),
            self.window])

class GenericWidget(rend.Fragment):
    
    def __init__(self, ID=None):
        self.children = []
        if ID is None:
            self.id = id(self)
        else:
            self.id = ID
            
    def append(self, w):
        self.children.append(w)

    def getDocFactory(self):
        print self.__class__.__name__
        return loaders.stan(self.getTag()[self.children])
    
    docFactory = property(getDocFactory)

# create evert tag class at runtime..
class _(GenericWidget):
    
    def __init__(self, **kwargs):
        if kwargs.has_key('id'):
            GenericWidget.__init__(self, kwargs['id'])
        else:
            GenericWidget.__init__(self)
        kwargs.update({'id':self.id})
        self.kwargs = kwargs
        
    def getTag(self):
        return getattr(x, self.tag)(**self.kwargs)

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
    g[t] = type(t, (_,), {'tag' : t.lower()})

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
        
    def getTag(self):
        return x.window(**self.kwargs)

