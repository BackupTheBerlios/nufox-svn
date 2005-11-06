# DO NOT RUN THIS IT WILL ALLOW PEOPLE TO DESTROY YOUR COMPUTER

from nufox import xul

from twisted.manhole import service


class Example(xul.XULPage):
    
    def setup(self):
        self.ns = {}
        self.window = xul.Window(height=400, width=400, title="Manhole")
        v = xul.VBox(flex=1)
        self.inbox = xul.TextBox(id='codeInput', flex=1)
        # XXX: Needs to be updated to use athena instead of livepage.
##         self.inbox.addHandler('onchange', self.codeSent,
##                      livepage.get('codeInput').value)

        self.outbox = xul.TextBox(
            id='output', rows=10, flex=1, readonly='true')
        hb = xul.HBox()
        hb.append(xul.Label(value=">>>"))
        hb.append(self.inbox)
        v.append(hb)
        v.append(self.outbox)
        self.window.append(v)

    def codeSent(self, value):
        self.inbox.setAttr('value', '') #clear the input
        result = service.runInConsole(value, None, globalNS=self.ns)
        if result is not None:
            d = self.outbox.getAttr('value')
            d.addCallback(self.updateOutput, repr(result))
         
    def updateOutput(self, result, oldResult):
        self.outbox.setAttr('value', oldResult + '\n' + result)
