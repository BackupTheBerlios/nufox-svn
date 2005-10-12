from nufox import xul

class Example(xul.XULPage):

    def setup(self):
        self.window = xul.Window(id="xul=window", 
        height=400, width=400,
        title="My Example")
        v = xul.VBox(flex=1)
        v.append(xul.Label(value="This message is from a mars"))
        v.append(xul.IFrame(src="http://google.com", flex=1))
        self.window.append(v)

