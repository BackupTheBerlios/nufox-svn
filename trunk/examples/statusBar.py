"""Contributed by Alagu Madhu"""

from nufox import xul


TEXT = (
    'Nufox is a framework for developing applications with the kind '
    'of graphical user interfaces that people expect from modern '
    'desktop applications.'
    )


class Example(xul.XULPage):
    
    def setup(self):
        self.window = xul.Window(
            title="NuFox Statusbar",
            style="background-color:#B3D4E5",
            )
        self.sampleDesc = xul.Description(
            value="NuFox StatusBar",
            style="font-weight: bold;font-size: 18pt",
            )
        self.mainLayout = xul.VBox(flex="1",style="overflow: auto")
        self.mainLayout.append(xul.Spacer(height="25"))
        self.mainLayout.append(self.sampleDesc)
        self.mainLayout.append(xul.Spacer(height="25"))
        self.statusbar = xul.StatusBar()
        self.statusbar.append(xul.StatusBarPanel(
            label=TEXT,
            flex="1",
            crop="right",
            ))
        self.statusbar.append(xul.StatusBarPanel(label="-tjs",crop="left"))
        self.window.append(self.mainLayout)
        self.window.append(self.statusbar)
