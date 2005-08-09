from nevow import livepage
from nufox import xul

class XULTKPage(xul.XULPage):

    def __init__(self):
        self.window = xul.Window(id="xul-window", height=400, width=400,
                                 title="Press this button!")
        v = xul.VBox(flex=2)
        b = xul.Button(id='sendCrap', label="A Button")
        v.append(b)
        v.append(xul.htmlns.img(
            src="http://trac.nunatak.com.au/trac/nufox-small.png"))
        self.window.append(v)

example = XULTKPage()
