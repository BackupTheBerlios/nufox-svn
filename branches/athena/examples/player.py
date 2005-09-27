from nufox import xul, composite
from nevow import static, livepage
from twisted.python.util import sibpath
livepage.DEBUG = True
class Example(xul.XULPage):

    def __init__(self):
        self.window = xul.Window(height=400, width=400,
                                 title="RealPlayer/HelixPlayer widget")
        v = xul.VBox(flex=1)
        #our player
        self.player = composite.Player('helixtest')
        #a group of controls
        controls = xul.HBox(flex=1)
        #some buttons
        play = xul.Button(label='play')
        play.addHandler('oncommand', self.playPushed)
        pause = xul.Button(label='pause')
        pause.addHandler('oncommand', self.pausePushed)
        stop = xul.Button(label='stop')
        stop.addHandler('oncommand', self.stopPushed)
        controls.append(play, pause, stop) 
        v.append(self.player, controls)
        self.window.append(v)

    def playPushed(self):
        self.player.play()
        
    def pausePushed(self):
        self.player.pause()
        
    def stopPushed(self):
        self.player.stop()

setattr(Example, 'child_helixtest',
    static.File(sibpath(__file__, 'helixtest.ogg'), 'application/ogg'))

example = Example()
