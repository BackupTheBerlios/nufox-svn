"""Nufox composite widgets.

Composite widgets manage collections of XUL elements for you. They
expose higher-level methods on the Python side, and reduce round trips
by using custom JavaScript on the XUL side.
"""


# XXX: Warning -- the following is for backwards-compatibility.
# Please begin importing composite widgets from the appropriate module
# of the nufox.composite package.

__all__ = [
    'Grid',
    'Player',
    'CompositeTreeBase',
    'SimpleTree',
    'NestedTree',
    ]

from nufox.composite.grid import Grid
from nufox.composite.player import Player
from nufox.composite.tree import Base as CompositeTreeBase
from nufox.composite.tree import Flat as SimpleTree
from nufox.composite.tree import Nested as NestedTree
