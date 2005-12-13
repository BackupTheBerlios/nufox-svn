from nufox.defer import defgen, wait
from twisted.internet.defer import DeferredList

from nufox.widget.base import Signal, Widget
from nufox.widget import signal, std
from nufox import xul


class DeckBrowser(std.Deck):
    """A specialized deck that acts like a web browser."""

    def setup(self):
        std.Deck.setup(self)
        self.curCanGoBack = False
        self.curCanGoForward = False

    def postSet_selectedIndex(self, index):
        return self._updateBackForward(index)

    def postSet_selectedPage(self, page):
        return self._updateBackForward(index)

    @defgen
    def addPage(self, page):
        # First, remove pages beyond the current index.
        index = wait(self.get('selectedIndex'))
        yield index
        index = index.getResult()
        toRemove = self.children[index + 1:]
        yield wait(DeferredList([
            self.removePage(rpage) for rpage in toRemove
            ]))
        # Next, add the new page.
        index = wait(std.Deck.addPage(self, page))
        yield index
        index = index.getResult()
        # Select the page after adding it.
        yield wait(self.set('selectedIndex', index))
        # Update back/forward.
        yield wait(self._updateBackForward(index))
        yield index

    @defgen
    def goBack(self):
        index = wait(self.get('selectedIndex'))
        yield index
        index = index.getResult()
        if index != 0:
            index = wait(self.set('selectedIndex', index - 1))
            yield index
            index = index.getResult()
            yield index
        else:
            yield None

    @defgen
    def goForward(self):
        index = wait(self.get('selectedIndex'))
        yield index
        index = index.getResult()
        if index + 1 < len(self.children):
            index = wait(self.set('selectedIndex', index + 1))
            yield index
            index = index.getResult()
            yield index
        else:
            yield None

    @defgen
    def _updateBackForward(self, curIndex):
        if curIndex == 0 and self.curCanGoBack:
            self.curCanGoBack = False
            yield wait(self.dispatch(signal.canGoBack, False))
        elif curIndex != 0 and not self.curCanGoBack:
            self.curCanGoBack = True
            yield wait(self.dispatch(signal.canGoBack, True))
        if curIndex + 1 == len(self.children) and self.curCanGoForward:
            self.curCanGoForward = False
            yield wait(self.dispatch(signal.canGoForward, False))
        elif curIndex + 1 < len(self.children) and not self.curCanGoForward:
            self.curCanGoForward = True
            yield wait(self.dispatch(signal.canGoForward, True))
        yield curIndex
