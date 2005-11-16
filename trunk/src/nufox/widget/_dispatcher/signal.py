"""A generic signal class."""


class _SIGNAL(type):
    """Base metaclass for signal classes."""

    def __str__(cls):
        return '<Signal: %s>' % (cls.__name__, )


class Signal(object):

    __metaclass__ = _SIGNAL

