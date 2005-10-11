from nufox import xul

class Example(xul.XULPage):

    def setup(self):
        self.window = xul.Window()
        self.browser = xul.IFrame(src="http://www.google.com", flex=1)
        self.button = xul.Button(label="get twisted")
        self.button.addHandler('oncommand', self.pushed)
        self.window.append(self.button, self.browser)

    def pushed(self):
        self.browser.setAttr('src', u'http://www.twistedmatrix.com')
