import os
from twisted.python import reflect
from nufox import xul

class NufoxExamples(xul.XULPage):

    def __init__(self):
        self.window = xul.Window(title='Nufox Examples')
        self.mainLayout = xul.HBox()
        self.leftPanel = xul.VBox(flex=20)
        self.display = xul.IFrame(flex=80, src="http://trac.nunatak.com.au/projects/nufox")
        self.mainLayout.append(self.leftPanel, self.display)
        self.window.append(self.mainLayout)
        
        for mod in os.listdir('examples'):
            if mod == '__init__.py' or not mod.endswith('py'):
                continue
            example = reflect.namedAny('examples.%s.example' % mod[:-3])
            self.putChild(mod[:-3], example)
            button = xul.Button(label=mod[:-3])
            button.addHandler('oncommand', self.selectExample)
            self.leftPanel.append(button)

    def selectExample(self, example):
        print "+++++++++++++", example
        self.display.setAttr('src', 'http://google.com')
        

from twisted.application import internet, service
from nevow import appserver


application = service.Application('xulstan')
#webServer = internet.TCPServer(8080, appserver.NevowSite(Examples()), 
#    interface='127.0.0.1')
webServer = internet.TCPServer(8080, appserver.NevowSite(NufoxExamples()))

webServer.setServiceParent(application)


