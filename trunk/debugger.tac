import os
from twisted.application import internet, service
from twisted.internet import reactor, utils
from nevow import appserver
from debugger.app import Debugger

def startApp():
    d = utils.getProcessOutput('/usr/bin/firefox',
        ['-chrome', 'http://localhost:8090'], os.environ)
    d.addCallback(endFox)

def endFox(r):
    print "Firefox died:",r 
    reactor.stop()
reactor.callLater(0, startApp)
application = service.Application('NuFox Debugger')
webServer = internet.TCPServer(8090, appserver.NevowSite(Debugger()), 
    interface='127.0.0.1')
webServer.setServiceParent(application)


