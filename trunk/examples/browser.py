from nufox import xul


class Example(xul.XULPage):
    """Browser Embedding"""

    def setup(self):
        self.window = xul.Window()
        self.browser = xul.IFrame(src=u"http://www.google.com", flex=1)
        self.button = xul.Button(label=u"get twisted")
        self.button.addHandler('oncommand', self.pushed)
        self.window.append(self.button, self.browser)

    def pushed(self):
        self.browser.setAttr(u'src', u'http://www.twistedmatrix.com')
