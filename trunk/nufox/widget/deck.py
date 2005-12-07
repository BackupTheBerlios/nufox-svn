from nufox.defer import defgen, wait
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

    @defgen
    def currentIndex(self):
        selectedIndex = wait(self.getAttr('selectedIndex'))
        yield selectedIndex
        selectedIndex = selectedIndex.getResult()
        yield _intOrZero(selectedIndex)

    @defgen
    def setCurrentIndex(self, index):
        yield wait(self.setAttr('selectedIndex', index))
        yield index

    @defgen
    def currentPage(self):
        currentIndex = wait(self.currentIndex())
        yield currentIndex
        currentIndex = currentIndex.getResult()
        yield self.children[currentIndex]

    @defgen
    def setCurrentPage(self, page):
        index = self.children.index(page)
        yield wait(self.setAttr('selectedIndex', index))
        yield page

    @defgen
    def addPage(self, page):
        yield wait(self.liveAppend(page))
        yield self.children.index(page)

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

    @defgen
    def setCurrentIndex(self, index):
        yield wait(Deck.setCurrentIndex(self, index))
        yield wait(self._updateBackForward(index))
        yield index

    @defgen
    def setCurrentPage(self, page):
        index = self.children.index(page)
        yield wait(self.setAttr('selectedIndex', index))
        yield wait(self._updateBackForward(index))
        yield page

    @defgen
    def addPage(self, page):
        # First, remove pages beyond the current index.
        index = wait(self.currentIndex())
        yield index
        index = index.getResult()
        toRemove = self.children[index + 1:]
        yield wait(DeferredList([
            self.removePage(page) for page in toRemove
            ]))
        # Next, add the new page.
        index = wait(Deck.addPage(self, page))
        yield index
        index = index.getResult()
        # Select the page after adding it.
        yield wait(self.setCurrentIndex(index))
        # Update back/forward.
        yield wait(self._updateBackForward(index))
        yield index

    @defgen
    def goBack(self):
        index = wait(self.currentIndex())
        yield index
        index = index.getResult()
        if index != 0:
            index = wait(self.setCurrentIndex(index - 1))
            yield index
            index = index.getResult()
            yield index
        else:
            yield None

    @defgen
    def goForward(self):
        index = wait(self.currentIndex())
        yield index
        index = index.getResult()
        if index + 1 < len(self.children):
            index = wait(self.setCurrentIndex(index + 1))
            yield index
            index = index.getResult()
            yield index
        else:
            yield None

    @defgen
    def _updateBackForward(self, curIndex):
        if curIndex == 0 and self.curCanGoBack:
            self.curCanGoBack = False
            yield wait(self.dispatch(self.canGoBack, False))
        elif curIndex != 0 and not self.curCanGoBack:
            self.curCanGoBack = True
            yield wait(self.dispatch(self.canGoBack, True))
        if curIndex + 1 == len(self.children) and self.curCanGoForward:
            self.curCanGoForward = False
            yield wait(self.dispatch(self.canGoForward, False))
        elif curIndex + 1 < len(self.children) and not self.curCanGoForward:
            self.curCanGoForward = True
            yield wait(self.dispatch(self.canGoForward, True))
        yield curIndex
