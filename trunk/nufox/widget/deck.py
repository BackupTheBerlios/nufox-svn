from twisted.internet.defer import DeferredList

from nufox.widget.base import Signal, Widget
from nufox import xul


def _intOrZero(value):
    if value:
        return int(value)
    return 0


class Deck(Widget):
    """Deck."""

    tag = 'deck'

    class pageSelected(Signal):
        """The deck's page was changed."""
        args = ('page', )

    def currentIndex(self):
        return self.getAttr('selectedIndex').addCallback(_intOrZero)

    def setCurrentIndex(self, index):
        def returnIndex(result):
            return index
        return self.setAttr('selectedIndex', index).addCallback(returnIndex)

    def currentPage(self):
        d = self.getAttr('selectedIndex').addCallback(_intOrZero)
        def toPage(index):
            return self.children[index]
        return d.addCallback(toPage)

    def setCurrentPage(self, page):
        index = self.children.index(page)
        d = self.setAttr('selectedIndex', index)
        def returnPage(result):
            return page
        return d.addCallback(returnPage)

    def addPage(self, page):
        d = self.liveAppend(page)
        def toIndex(result):
            return self.children.index(page)
        d.addCallback(toIndex)
        return d

    def removePage(self, page):
        return self.remove(page)

    def indexForPage(self, page):
        return self.children.index(page)

    def pageForIndex(self, index):
        return self.children[index]


class DeckBrowser(Deck):
    """A specialized deck that acts like a web browser."""

    tag = 'deck'

    class canGoBack(Signal):
        """Argument is True if the deck can go back one page."""
        args = ('can', )

    class canGoForward(Signal):
        """Argument is False if the deck can go forward one page."""
        args = ('can', )

    def setup(self):
        Deck.setup(self)
        self.curCanGoBack = False
        self.curCanGoForward = False

    def setCurrentIndex(self, index):
        return Deck.setCurrentIndex(self, index).addCallback(
            self._updateBackForward)

    def setCurrentPage(self, page):
        index = self.children.index(page)
        d = self.setAttr('selectedIndex', index)
        def update(result):
            return self._updateBackForward(index)
        d.addCallback(update)
        def returnPage(result):
            return page
        return d.addCallback(returnPage)

    def addPage(self, page):
        # First, remove pages beyond the current index.
        d = self.currentIndex()
        def removePages(index):
            toRemove = self.children[index + 1:]
            def returnIndex(result):
                return index
            return DeferredList([
                self.removePage(page) for page in toRemove
                ]).addCallback(returnIndex)
        d.addCallback(removePages)
        # Next, add the new page.
        def addPage(result):
            d = Deck.addPage(self, page)
            return d
        d.addCallback(addPage)
        # Select the page after adding it.
        d.addCallback(self.setCurrentIndex)
        # Update back/foward.
        d.addCallback(self._updateBackForward)
        return d

    def goBack(self):
        d = self.currentIndex()
        def go(index):
            if index == 0:
                pass
            else:
                return self.setCurrentIndex(index - 1)
        return d.addCallback(go)

    def goForward(self):
        d = self.currentIndex()
        def go(index):
            if index + 1 == len(self.children):
                pass
            else:
                return self.setCurrentIndex(index + 1)
        return d.addCallback(go)

    def _updateBackForward(self, curIndex):
        if curIndex == 0 and self.curCanGoBack:
            self.curCanGoBack = False
            self.dispatch(self.canGoBack, False)
        elif curIndex != 0 and not self.curCanGoBack:
            self.curCanGoBack = True
            self.dispatch(self.canGoBack, True)
        if curIndex + 1 == len(self.children) and self.curCanGoForward:
            self.curCanGoForward = False
            self.dispatch(self.canGoForward, False)
        elif curIndex + 1 < len(self.children) and not self.curCanGoForward:
            self.curCanGoForward = True
            self.dispatch(self.canGoForward, True)
        return curIndex
