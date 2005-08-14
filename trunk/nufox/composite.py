"""These are composite widgets, that is, widgets composed of more than one 
XUL element, with special methods, and custom JS."""

from nufox import xul
from nevow import livepage



class Player(xul.GenericWidget):
    """I am a media player, I require either the helix or realplayer plugin"""

    def __init__(self, mediaURL, width=300, height=300):
        xul.GenericWidget.__init__(self)
        newKwargs = {
            'src' : mediaURL,
            'width' : width,
            'height' : height,
            'console' : 'one',
            'controls' : 'ImageWindow',
            'maintainaspect' : 'true' }
        self.kwargs = newKwargs

    def play(self):
        self.pageCtx.client.send(livepage.js.PlayerPlay(str(self.id)))

    def pause(self):
        self.pageCtx.client.send(livepage.js.PlayerPause(str(self.id))) 

    def stop(self):
        self.pageCtx.client.send(livepage.js.PlayerStop(str(self.id)))

    def getTag(self):
        return xul.htmlns.embed(**self.kwargs)
