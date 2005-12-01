from nufox.widget.box import VBox
from nufox.widget.button import Button
from nufox.widget.label import Label
from nufox.widget.window import Window
from nufox import xul


class Example(xul.XULPage):
    """nufox.widget: Closing widgets"""

    def setup(self):
        # Create the window.
        window = self.window = Window()
        # Create a box to layout our widgets.
        vbox = window.adopt(VBox(flex=1))
        # Create a button to push.
        button = self.button = vbox.adopt(
            Button(label=u'Push to close the box below.'))
        # Create an inner box with a label.
        innerVbox = self.innerVbox = vbox.adopt(VBox(flex=1))
        label = innerVbox.adopt(Label(value=u'This will close...'))
        # Close the inner box when the button is clicked.
        button.connect(button.clicked, innerVbox.close)
        # Update the button when the inner box is closed.
        innerVbox.connect(innerVbox.closed, self.on_innerVbox_closed)

    def on_innerVbox_closed(self):
        button = self.button
        button.setAttr('label', u'Widget was closed')
        button.disconnect(button.clicked, self.innerVbox.close)
        del self.innerVbox

