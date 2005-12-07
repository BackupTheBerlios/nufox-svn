import louie

class Signal(louie.Signal):
    pass


class changed(Signal):
    """The value was changed."""
    args = ('value', )


class clicked(Signal):
    """The widget was clicked."""
    args = ()


class closed(Signal):
    """The widget was closed."""
    args = ()


class jsOnclick(Signal):
    """A Javascript onclick event was received."""
    args = ()


class jsOncommand(Signal):
    """A Javascript oncommand event was received."""
    args = ()
