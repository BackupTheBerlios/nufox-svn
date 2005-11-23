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


# Copyright (C) 2001-2005 Orbtech, L.L.C.
#
# Schevo
# http://schevo.org/
#
# Orbtech
# 709 East Jackson Road
# Saint Louis, MO  63119-4241
# http://orbtech.com/
#
# This toolkit is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This toolkit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
