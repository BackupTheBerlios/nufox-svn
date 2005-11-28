import os
import sys
if os.name == 'nt':
    from twisted.internet import win32eventreactor
    win32eventreactor.install()

from twisted.application import app,service
import twisted.python.log

from nufox import deploy

from examples import _base


if __name__ == '__main__':
    application = deploy.NufoxDesktopApp(_base.NufoxExamples)
    if not sys.argv[1:2] == ['-q']:
        twisted.python.log.startLogging(sys.stdout)
    service.IService(application).startService()
    from twisted.internet import reactor
    reactor.run()
