# DO NOT RUN THIS IT WILL ALLOW PEOPLE TO DESTROY YOUR COMPUTER

from nufox import xul
from nevow import livepage

from twisted.manhole import service

class Manhole(xul.XULPage):
    def __init__(self):
        self.ns = {}
        self.window = xul.Window(id="xul-window", height=400, width=400,
                                 title="Manhole")
        v = xul.VBox(flex=1)
        t = xul.TextBox(id='codeInput', flex=1)
        t.addHandler('onchange', 'codeSent',
                     livepage.document.getElementById('codeInput').value)

        self.out = xul.TextBox(id='output', rows=10, flex=1, readonly='true')
        hb = xul.HBox()
        hb.append(xul.Label(value=">>>"))
        hb.append(t)
        v.append(hb)
        v.append(self.out)
        self.window.append(v)

    def handle_codeSent(self, arg, value):
        result = service.runInConsole(value, None, globalNS=self.ns)
        d = self.out.getAttr(self.client, 'value')
        d.addCallback(self.updateOutput, repr(result))
    
    def updateOutput(self, result, oldResult):
        self.out.setAttr(self.client, 'value', oldResult + '\n' + result)

example = Manhole()
