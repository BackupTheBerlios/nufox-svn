"""Common plugins for PyDispatcher."""

from nufox.widget._dispatcher import dispatcher


class QtWidget(dispatcher.Plugin):
    """A Plugin for PyDispatcher that knows how to handle Qt widgets
    when using PyQt built with SIP 4 or higher.

    Weak references are not useful when dealing with QWidget
    instances, because even after a QWidget is closed and destroyed,
    only the C++ object is destroyed.  The Python 'shell' object
    remains, but raises a RuntimeError when an attempt is made to call
    an underlying QWidget method.

    This plugin alleviates this behavior, and if a QWidget instance is
    found that is just an empty shell, it prevents PyDispatcher from
    dispatching to any methods on those objects.
    """

    def __init__(self):
        try:
            import qt
        except ImportError:
            self.is_live = self._is_live_no_qt
        else:
            self.qt = qt

    def is_live(self, receiver):
        """If receiver is a method on a QWidget, only return True if
        it hasn't been destroyed."""
        if (hasattr(receiver, 'im_self') and
            isinstance(receiver.im_self, self.qt.QWidget)
            ):
            try:
                receiver.im_self.x()
            except RuntimeError:
                return False
        return True

    def _is_live_no_qt(self, receiver):
        return True
