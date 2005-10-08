from nevow import livepage
from nufox import xul

class Example(xul.XULPage):
    def __init__(self):
        self.counter = 0
        self.window = xul.Window(id="xul-window", height=400, width=400,
                                 title="XUL is Cool")
        self.box = xul.VBox(flex=1)

        b = xul.Button(label="The Give Me More Button")
        b.addHandler('oncommand', self.buttonPushed)
        self.box.append(b)

        self.box.append(xul.Label(value="Pre go live label"))

        self.window.append(self.box)

    def buttonPushed(self):
        self.box.append(xul.Label(value="Post go live label"))
