# DO NOT RUN THIS IT WILL ALLOW PEOPLE TO DESTROY YOUR COMPUTER
USE = False


from nufox import xul

from twisted.manhole import service


class Example(xul.XULPage):
    """Manhole"""

    if USE:
        def setup(self):
            self.ns = {}
            self.window = xul.Window(height=400, width=400, title=u"Manhole")
            v = xul.VBox(flex=1)
            self.inbox = xul.TextBox(id=u'codeInput', flex=1)
            # XXX: Needs to be updated to use athena instead of livepage.
    ##         self.inbox.addHandler('onchange', self.codeSent,
    ##                      livepage.get('codeInput').value)

            self.outbox = xul.TextBox(
                id=u'output', rows=10, flex=1, readonly=u'true')
            hb = xul.HBox()
            hb.append(xul.Label(value=u">>>"))
            hb.append(self.inbox)
            v.append(hb)
            v.append(self.outbox)
            self.window.append(v)

        def codeSent(self, value):
            self.inbox.setAttr(u'value', u'') #clear the input
            result = service.runInConsole(value, None, globalNS=self.ns)
            if result is not None:
                d = self.outbox.getAttr(u'value')
                d.addCallback(self.updateOutput, repr(result))

        def updateOutput(self, result, oldResult):
            self.outbox.setAttr(u'value', oldResult + u'\n' + result)

    else: # not USE
        def setup(self):
            self.window = xul.Window(title=u'Manhole (disabled)')
