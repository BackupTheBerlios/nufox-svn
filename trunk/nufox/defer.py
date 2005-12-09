"""Nufox-specific extensions to Twisted's deferredGenerator and
waitForDeferred."""

import inspect

from twisted.internet.defer import DeferredList
from twisted.internet.defer import waitForDeferred as wait
from twisted.internet.defer import _deferGenerator
from twisted.python.util import mergeFunctionMetadata


def defgen(f):
    """Specialized deferredGenerator."""
    def unwindGenerator(*args, **kwargs):
        # Ignore kwargs that aren't in f's arg spec.  This is useful
        # for ignoring extra arguments for functions that act as Louie
        # signal receivers.
        func_args = inspect.getargs(f.func_code)
        newKwargs = {}
        for key, value in kwargs.iteritems():
            if key in func_args:
                newKwargs[key] = value
        return _deferGenerator(f(*args, **newKwargs))
    return mergeFunctionMetadata(f, unwindGenerator)


def dlist(*deferreds):
    """Shortcut for DeferredList([deferreds])."""
    return DeferredList(deferreds)
