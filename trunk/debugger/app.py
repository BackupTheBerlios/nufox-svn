from nufox import xul

class Debugger(xul.XULPage):
    js = """
netscape.security.PrivilegeManager.enablePrivilege('UniversalXPConnect');
const MEDIATOR_CONTRACTID="@mozilla.org/appshell/window-mediator;1";
const nsIWindowMediator=Components.interfaces.nsIWindowMediator;
var windowManager= Components.classes[MEDIATOR_CONTRACTID].getService(nsIWindowMediator);
alert(windowManager);
    """
    def __init__(self):
        self.counter = 0
        self.window = xul.Window(height=600, width=800, title="NuFox Debugger")
        v = xul.VBox(flex=1)
        v.append(xul.Label(value='NuFox Debugger'))
        h = xul.HBox(flex=1)
        h.append(self.makeLeftFrame())
        splitter = xul.Splitter(collapse='before', resizeafter='farthest')
        splitter.append(xul.Grippy())
        h.append(splitter)
        h.append(self.makeRightFrame())
        v.append(h)
        self.window.append(v)

    def makeLeftFrame(self):
        box = xul.VBox(flex=20)
        box.append(xul.Label(value="debugger"))
        return box
    
    def makeRightFrame(self):
        box = xul.VBox(flex=80)
        self.previewFrame = xul.IFrame(src='about:blank', flex=1)
        self.debugOutput = xul.TextBox(flex=1)
        box.append(self.previewFrame)
        box.append(self.debugOutput)
        return box
#    def handle_buttonPushed(self, cli):
#        self.counter += 1
#        self.label.setAttr(self.client, 
#            'value', 'You have clicked %s times' % ( self.counter,))
#        d = self.label.getAttr(self.client, 'value')
#        d.addBoth(log)
