from nufox.defer import defgen, wait
from nufox.functional import partial
from nufox.widget.window import Window
from nufox.widget import signal, std
from nufox import xul


class Example(xul.XULPage):
    """nufox.widget: Basic usage"""

    def setup(self):
        # Keep track of how many times pushed.
        self.counter = 0
        # Create the window.
        window = self.window = Window(title=u'Press this button!')
        # Create a box to layout our widgets.
        vbox = std.VBox(flex=1)
        window.append(vbox)
        # Create a button to push.
        button = std.Button(label=u'A Button')
        # Respond to its ``clicked`` signal.
        button.connect(signal.clicked, self.on_button_clicked)
        # Create a label to update upon clicking.
        label = self.label = std.Label(value=u'Hello there')
        label2 = std.Label(value=u'(the above line will be repeated below)')
        label3 = self.label3 = std.Label()
        vbox.append(button, label, label2, label3)
        # Connect the ``changed`` signal from ``label`` directly to
        # the setting of the ``value`` attribute on ``label3``.
        label.connect(signal.changed, partial(label3.set, 'value'))

    def on_button_clicked(self):
        self.counter += 1
        # Set the label's value.  Don't bother returning it, because
        # it doesn't need to be linked back into any sequential chain
        # of events.
        self.label.set('value', u'You have clicked %s times' % self.counter)
