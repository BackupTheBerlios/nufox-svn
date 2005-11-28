# Install a singleton async receiver for Louie.

__all__ = []

from nufox.widget._dispatcher.dispatcher import plugins
from nufox.widget._dispatcher.plugin import AsyncReceiver

plugins.append(AsyncReceiver())

