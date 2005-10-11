from nevow import livepage
from nufox import xul

class Example(xul.XULPage):

    def setup(self):
        self.counter = 0
        self.window = xul.Window(height=400, width=400, title="keybindings")
        v = xul.VBox(flex=1)
        self.ks = xul.KeySet()
        shift_i = xul.Key(modifiers='alt', _key='I')
        shift_i.addHandler('oncommand', self.shift_i_pressed)
        self.ks.append(shift_i)
        self.ks.append(xul.Key(keycode='VK_ESCAPE', oncommand='window.close();'))
        self.window.append(self.ks)
        self.label = xul.Label(value=self.counter) 
        v.append(xul.Label(value='Press "alt+i" to increment the number'))
        v.append(xul.Label(value='Press "Esc" to close the window.'))
        v.append(self.label)
        self.window.append(v)

    def shift_i_pressed(self):
        self.counter += 1
        self.label.setAttr('value', 
            'You have clicked %s times' % ( self.counter,))

