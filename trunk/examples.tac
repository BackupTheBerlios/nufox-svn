import os
from twisted.python import reflect
from nufox import xul

class NufoxExamples(xul.XULPage):

    def __init__(self):
        self.window = xul.Window(title='Nufox Examples')
        self.mainLayout = xul.HBox(flex=1)
        self.leftPanel = xul.VBox(flex=20)
        self.display = xul.IFrame(flex=80, src="http://trac.nunatak.com.au/projects/nufox")
        self.mainLayout.append(self.leftPanel, self.display)
        self.window.append(self.mainLayout)

        for mod in os.listdir('examples'):
            if mod == '__init__.py' or not mod.endswith('.py'):
                continue
            modID = mod[:-3]
            example = reflect.namedAny('examples.%s.example' % modID)
            self.putChild(modID, example)
            button = xul.Button(label=modID)
            button.addHandler('oncommand', 
                lambda modID=modID: self.selectExample(modID))
            self.leftPanel.append(button)

    def selectExample(self, example):
        url = 'http://localhost:8080/%s' %(example,)
        print "LOADING EXAMPLE FROM:", url, ' so there.'
        self.display.setAttr('src', url)


from twisted.application import internet, service
from nevow import appserver


application = service.Application('xulstan')
#webServer = internet.TCPServer(8080, appserver.NevowSite(Examples()),
#    interface='127.0.0.1')
webServer = internet.TCPServer(8080, appserver.NevowSite(NufoxExamples()))

webServer.setServiceParent(application)


