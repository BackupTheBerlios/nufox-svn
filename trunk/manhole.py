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
        b = xul.Button(id='sendCode', label='Send Code')
        b.addHandler('oncommand', 'codeSent',
                     livepage.document.getElementById('codeInput').value)
        t = xul.TextBox(id='codeInput')
        self.out = xul.TextBox(id='output')
        v.append(t)
        v.append(b)
        v.append(self.out)
        self.window.append(v)

    def handle_codeSent(self, arg, value):
        result = service.runInConsole(value, None, globalNS=self.ns)
        print result
        result = repr(result)
        return livepage.assign(livepage.get('output').value, result)

example = Manhole()
