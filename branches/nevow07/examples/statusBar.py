from nufox import xul


TEXT = (
    u'Nufox is a framework for developing applications with the kind '
    u'of graphical user interfaces that people expect from modern '
    u'desktop applications.'
    )


class Example(xul.XULPage):
    """Status Bar"""

    discussion = """
    Contributed by Alagu Madhu.
    """
    
    def setup(self):
        self.window = xul.Window(
            title=u"NuFox Statusbar",
            style=u"background-color:#B3D4E5",
            )
        self.sampleDesc = xul.Description(
            value=u"NuFox StatusBar",
            style=u"font-weight: bold;font-size: 18pt",
            )
        self.mainLayout = xul.VBox(flex=1,style=u"overflow: auto")
        self.mainLayout.append(xul.Spacer(height=u"25"))
        self.mainLayout.append(self.sampleDesc)
        self.mainLayout.append(xul.Spacer(height=u"25"))
        self.statusbar = xul.StatusBar()
        self.statusbar.append(xul.StatusBarPanel(
            label=TEXT,
            flex=1,
            crop=u"right",
            ))
        self.statusbar.append(xul.StatusBarPanel(label=u"-tjs",crop=u"left"))
        self.window.append(self.mainLayout)
        self.window.append(self.statusbar)
