from nevow import livepage
from nufox import xul

class XULTKPage(xul.XULPage):

    def __init__(self):
        self.counter = 0
        self.window = xul.Window(id="xul=window", height=400, width=400,
        title="Press this button!")
        v = xul.VBox(flex=1)
        b = xul.Button(label="A Button", tooltiptext="Press me!")
        b.addHandler('oncommand', self.buttonPushed)
        self.label = xul.Label(value='hello there')
        v.append(b)
        v.append(self.label)
        self.window.append(v)

    def buttonPushed(self, cli):
        self.counter += 1
        self.label.setAttr(self.client, 'value', 
            'You have clicked %s times' % ( self.counter,))
        
example = XULTKPage()
