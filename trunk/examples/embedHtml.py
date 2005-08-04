from nevow import livepage
from nufox import xul, xmlstan

class XULTKPage(xul.XULPage):

    def __init__(self):
        self.window = xul.Window(id="xul-window", height=400, width=400,
                                 title="Press this button!", 
            h=xmlstan.xmlns("http://www.w3.org/1999/xhtml"))
        v = xul.VBox(flex=2)
        b = xul.Button(id='sendCrap', label="A Button")
        b.addHandler('oncommand', 'buttonPushed')
        htmlChunk = xul.htmlns.img(
            src="http://trac.nunatak.com.au/trac/nufox-small.png")
        img = xul.Image( 
            src="http://trac.nunatak.com.au/trac/nufox-small.png")
        v.append(b)
        v.append(htmlChunk)
        
        self.window.append(v)

example = XULTKPage()
