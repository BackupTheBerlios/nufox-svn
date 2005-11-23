from nufox.widget.button import Button
from nufox.widget.label import Label
from nufox.widget.window import Window
from nufox import xul


class Example(xul.XULPage):
    """nufox.widget: Basic usage"""

    def setup(self):
        # Keep track of how many times pushed.
        self.counter = 0
        # Create the window.
        window = self.window = Window(title=u'Press this button!')
        # Create a box to layout our widgets.
        vbox = xul.VBox(flex=1)
        window.append(vbox)
        # Create a button to push.
        button = Button(label=u'A Button')
        # Respond to its `clicked` signal.
        button.connect(button.clicked, self.on_button_clicked)
        # Create a label to update upon clicking.
        label = self.label = Label(value=u'Hello there')
        label2 = Label(value=u'(the above line will be repeated below)')
        label3 = self.label3 = Label()
        vbox.append(button, label, label2, label3)
        # Connect the `changed` signal from `label` directly to the
        # `setValue` method on `label3`.
        label.connect(label.changed, label3.setValue)

    def on_button_clicked(self):
        self.counter += 1
        # Set the label's value.
        self.label.setValue(
            u'You have clicked %s times' % self.counter,
            )
        # Event handlers don't return anything of meaning.  If you
        # need to store the value of a deferred for later inspection,
        # you must contain it somewhere, i.e. as an attribute of an
        # object or an item in a list.

