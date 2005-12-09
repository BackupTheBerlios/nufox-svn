import louie

class Signal(louie.Signal):
    pass


class changed(Signal):
    """The value was changed."""
    args = ('value', )


class canGoBack(Signal):
    """Argument is True if a browser can go back one page."""
    args = ('can', )


class canGoForward(Signal):
    """Argument is False if a browser can go forward one page."""
    args = ('can', )


class clicked(Signal):
    """The widget was clicked."""
    args = ()


class closed(Signal):
    """The widget was closed."""
    args = ()


class jsOnclick(Signal):
    """A Javascript onclick event was received."""
    args = ()


class jsOndblclick(Signal):
    """A Javascript ondblclick event was received."""
    args = ()


class jsOncommand(Signal):
    """A Javascript oncommand event was received."""
    args = ()
