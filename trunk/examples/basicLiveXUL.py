from nevow import livepage
from nufox import xul

class XULTKPage(xul.XULPage):

    def __init__(self):
        self.counter = 0
        self.window = xul.Window(id="xul-window", height=400, width=400,
                                 title="Press this button!")
        v = xul.VBox(flex=1)
        b = xul.Button(id='sendCrap', label="A Button")
        b.addHandler('oncommand', 'buttonPushed')
        self.label = xul.Label(value='hello there')
        v.append(b)
        v.append(self.label)
        self.window.append(v)

    def handle_buttonPushed(self, cli):
        print "HHHHHHHHHHHHHHHHHHHHHHHHHEY"
        self.counter += 1
        return livepage.assign(livepage.get(str(id(self.label))).value,
            'You have clicked %s times' % ( self.counter,))                               

        
example = XULTKPage()
