from nufox.widget.base import Signal, Widget


class Box(Widget):
    """Box."""

    tag = 'box'


class HBox(Box):
    """Horizontally-oriented box."""

    tag = 'hbox'


class VBox(Box):
    """Vertically-oriented box."""

    tag = 'vbox'

