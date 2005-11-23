import os

from twisted.python import log, reflect, util

from nevow import rend, loaders, tags, static

from nufox import deploy
from nufox.widget.window import Window
from nufox import xul


def splitNerdyCaps(s):
    wordBuffer = []
    currentWord = []
    for c in s:
        if c.isupper() or c.isdigit():
            if len(currentWord) != 0:
                wordBuffer.append(''.join(currentWord))
                currentWord = []
        currentWord.append(c)
    if len(currentWord) != 0:
        wordBuffer.append(''.join(currentWord))
    return ' '.join([w.capitalize() for w in wordBuffer])


class Sources(rend.Page):
    # Borrowed from Nevow's examples.tac
    
    def __init__(self, path, _):
        rend.Page.__init__(self, path)

    def render_htmlizer(self, ctx, path):
        from twisted.python import htmlizer
        from StringIO import StringIO
        output = StringIO()
        htmlizer.filter(open(path), output, writer=htmlizer.SmallerHTMLWriter)
        return tags.xml(output.getvalue())

    docFactory = loaders.stan(
    tags.html[
        tags.head[
            tags.title[u'Python source file: ', str],
            tags.link(type='text/css', rel='stylesheet', href='/cssfile')],
        tags.body[
            render_htmlizer]])


class ExampleViewer(xul.XULPage):

    liveChildren = {}

    def setup(self):
        # Get metadata about the example.
        example = self.example
        moduleId = example.moduleId
        self.__doc__ = example.__doc__ or 'No Description'
        doc = unicode(self.__doc__)
        title = example.title
        discussion = unicode(getattr(example, 'discussion', u'No Discussion'))
        # Create the outer tab box.
        window = self.window = Window(title=title)
        tabBox = xul.TabBox(flex=1)
        window.append(tabBox)
        tabs = xul.Tabs()
        tabBox.append(tabs)
        for label in [u'Example', u'Source', u'Discussion']:
            tabs.append(xul.Tab(label=label))
        panels = xul.TabPanels(flex=1)
        tabBox.append(panels)
        # Create the 'Example' tab panel.
        example = xul.IFrame(flex=1, src='example/')
        panels.append(example)
        # Create the 'Source' tab panel.
        sources = xul.IFrame(flex=1, src='/sources/%s.py' % moduleId)
        panels.append(sources)
        # Create the 'Discussion' tab panel.
        discussionBox = xul.VBox(flex=1)
        panels.append(discussionBox)
        groupBox = xul.GroupBox()
        discussionBox.append(groupBox)
        docLabel = xul.Label().append(doc)
        groupBox.append(docLabel)
        discussionLabel = xul.Label().append(discussion)
        discussionBox.append(discussionLabel)


def getExamples():
    liveChildren = {}
    for mod in os.listdir(util.sibpath(__file__, '.')):
        if mod.startswith('_') or not mod.endswith('.py'):
            continue
        moduleId = mod[:-3]
        print "Found example 'examples.%s.example'" % (moduleId,)
        example = reflect.namedAny('examples.%s.Example' % (moduleId,))
        class Viewer(ExampleViewer):
            pass
        example.moduleId = moduleId
        doc = unicode(example.__doc__)
        title = getattr(example, 'title', None)
        if not title:
            if doc:
                # Take the first line of the docstring.
                title = u''.join(doc.split(u'\n')[:1])
            else:
                title = splitNerdyCaps(moduleId)
        example.title = title
        Viewer.example = example
        Viewer.liveChildren = {'example': example}
        liveChildren[moduleId] = Viewer
    return liveChildren


class NufoxExamples(xul.XULPage):
    
    liveChildren = getExamples()

    child_sources = static.File('examples', defaultType='text/plain')
    child_sources.processors['.py'] = Sources
    child_sources.contentTypes = {}
    child_cssfile = static.File('examples/index.css')
    child_docs = static.File(util.sibpath(__file__, '../doc/html'))

    def setup(self):
        window = self.window = Window(title=u'Nufox Examples')
        popupset = self.popupset = xul.PopupSet()
        mainLayout = self.mainLayout = xul.HBox(flex=1)
        leftSide = self.leftSide = xul.VBox(flex=10)
        linkBox = self.linkBox = xul.ListBox(rows=3)
        exampleBox = self.exampleBox = xul.ListBox(flex=1)
        leftSide.append(
            xul.Label(value=u'Nufox Links'),
            linkBox,
            xul.Label(value=u'Examples'),
            exampleBox,
            )
        display = self.display = xul.IFrame(
            flex=90, src='docs/introduction.html')
        mainLayout.append(leftSide, display)
        window.append(self.popupset, mainLayout)
        # List of standard Nufox information.
        linkBox.addHandler('onselect', self.linkClicked)
        website = xul.ListItem(
            label=u'Nufox Website',
            value='http://trac.nunatak.com.au/projects/nufox',
            tooltip=u'Nufox Website')
        docs = xul.ListItem(
            label=u'Documentation',
            value='docs/index.html',
            tooltip=u'Nufox Documentation',
            )
        linkBox.append(docs, website)
        # List of examples.
        exampleBox.addHandler('onselect', self.exampleClicked)
        for (moduleId, exampleViewer) in sorted(self.liveChildren.items()):
            ttID = 'tt_%s' % (moduleId,)
            puID = 'pu_%s' % (moduleId,)
            li = xul.ListItem(
                label=exampleViewer.example.title,
                value='%s/' % moduleId,
                tooltip=ttID,
                context=puID,
                )
            exampleBox.append(li)
            tt = xul.ToolTip(
                id=ttID,
                orient='vertical',
                style='background-color: #33DD00;'
                )
            tt.append(xul.Label(
                value=exampleViewer.__doc__ or u'No Description'))
            popupset.append(tt)

    def exampleClicked(self):
        self.exampleBox.getAttr('value').addCallbacks(self.selectLink, log.err)

    def linkClicked(self):
        self.linkBox.getAttr('value').addCallbacks(self.selectLink, log.err)

    def selectLink(self, url):
        self.display.setAttr('src', url)


