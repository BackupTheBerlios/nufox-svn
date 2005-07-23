from nufox import xul

class XULTKPage(xul.XULPage):
    js = """

    function sayHi(count) {
        alert("Hi! you have pressed me "+count+" times!");
    }
    """
    jsFuncs = ['sayHi']
    
    def __init__(self):
        self.counter = 0
        self.window = xul.Window(id="xul=window", height=400, width=400,
        title="Press this button!")
        v = xul.VBox(flex=1)
        b = xul.Button(label="press me!")
        b.addHandler('oncommand', self.buttonPushed)
        self.window.append(v.append(b))

    def buttonPushed(self, cli):
        self.counter += 1
        cli.call(self.sayHi, self.counter)
        
example = XULTKPage()
