"""Nufox media player widget."""

from nufox import xul


class Player(xul.GenericWidget):
    """Helix/RealPlayer-based media player.

    Requires Helix or RealPlayer plugin to be installed in Mozilla."""

    def __init__(self, mediaURL, width=300, height=300):
        xul.GenericWidget.__init__(self)
        newKwargs = {
            'src' : mediaURL,
            'width' : width,
            'height' : height,
            'console' : u'one',
            'controls' : u'ImageWindow',
            'maintainaspect' : u'true' }
        self.kwargs = newKwargs

    def play(self):
        self.callRemote('PlayerPlay', self.id)
##         self.pageCtx.client.send(livepage.js.PlayerPlay(str(self.id)))

    def pause(self):
        self.callRemote('PlayerPause', self.id)
##         self.pageCtx.client.send(livepage.js.PlayerPause(str(self.id)))

    def stop(self):
        self.callRemote('PlayerStop', self.id)
##         self.pageCtx.client.send(livepage.js.PlayerStop(str(self.id)))

    def getTag(self):
        return xul.htmlns.embed(**self.kwargs)


