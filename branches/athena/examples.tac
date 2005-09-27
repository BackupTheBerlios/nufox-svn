import os
from twisted.python import reflect, log, util
from twisted.internet import utils as tiutils
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


###################################
#Liberated from nevow examples.tac
###################################

from nevow import rend, loaders, tags, static

class Sources(rend.Page):
    def __init__(self, path, _):
        rend.Page.__init__(self, path)

    def render_htmlizer(self, ctx, path):
        from twisted.python import htmlizer
        from StringIO import StringIO
        output = StringIO()
        try:
            htmlizer.filter(open(path), output, writer=htmlizer.SmallerHTMLWriter)
        except AttributeError:
            output = StringIO("""Starting after Nevow 0.4.1 Twisted
2.0 is a required dependency. Please install it""")
        return tags.xml(output.getvalue())

    docFactory = loaders.stan(
    tags.html[
        tags.head[
            tags.title["Python source file: ", str],
            tags.link(type='text/css', rel='stylesheet', href='/cssfile')],
        tags.body[
            render_htmlizer]])

#################################
#End the liberation, thanks guys
#################################

class NufoxExamples(xul.XULPage):

    child_sources = static.File('examples', defaultType='text/plain')
    child_sources.processors['.py'] = Sources
    child_sources.contentTypes = {}
    child_cssfile = static.File('examples/index.css')
    child_docs = static.File(util.sibpath(__file__, 'doc/html'))
    
    def __init__(self):
        self.window = xul.Window(title='Nufox Examples')
        self.popupset = xul.PopupSet()
        self.mainLayout = xul.HBox(flex=1)
        self.leftSide = xul.VBox(flex=10)
        self.linkBox = xul.ListBox(rows=3)
        self.exampleBox = xul.ListBox(flex=1)
        self.leftSide.append(xul.Label(value="Nufox Links"),
                             self.linkBox,
                             xul.Label(value="Examples (right click)"),
                             self.exampleBox)
        self.display = xul.IFrame(flex=90, src="docs/introduction.html")
        self.mainLayout.append(self.leftSide, self.display)
        self.window.append(self.popupset, self.mainLayout)
        
        website = xul.ListItem(label="Nufox Website", 
                               value='http://trac.nunatak.com.au/projects/nufox', 
                            tooltip="Nufox Website")

        docs = xul.ListItem(label="Documentation", 
                            value='http://localhost:8080/docs/index.html', 
                            tooltip="Nufox Documentation")
        self.linkBox.append(docs, website)
        self.linkBox.addHandler('onselect', self.linkClicked)

        for mod in os.listdir(util.sibpath(__file__,'examples')):
            if mod == '__init__.py' or not mod.endswith('.py'):
                continue
            modID = mod[:-3]
            ttID = 'tt_%s' % (modID,)
            puID = 'pu_%s' % (modID,)
            print "Finding example 'examples.%s.example'" % (modID,) 
            example = reflect.namedAny('examples.%s.example' % (modID,))
            self.putChild(modID, example)
            li = xul.ListItem(label=splitNerdyCaps(modID), value='0', 
                              tooltip=ttID, 
                              context=puID)
            self.exampleBox.append(li)
            tt = xul.ToolTip(id=ttID, orient="vertical", 
                style="background-color: #33DD00;").append(
                    xul.Label(
                        value=example.__doc__ or "No Description"))
            viewExample = xul.MenuItem(label='View Example')
            viewSource = xul.MenuItem(label='View Source')
            viewExample.addHandler('oncommand', self.selectExample, modID)
            viewSource.addHandler('oncommand', self.selectSource, modID)
            pu = xul.Popup(id=puID).append(viewExample, viewSource)
            self.popupset.append(tt, pu) 
        
    def selectExample(self, example):
        url = 'http://localhost:8080/%s' %(example,)
        self.display.setAttr('src', url)

    def selectSource(self, modID):
        url = 'http://localhost:8080/sources/%s.py' %(modID,)
        self.display.setAttr('src', url)

    def linkClicked(self):
        self.linkBox.getAttr('value').addCallbacks(self.selectLink,
                                                   log.err)

    def selectLink(self, url):
            self.display.setAttr('src', url)


from twisted.application import internet, service
from nevow import appserver


application = service.Application('xulstan')
webServer = internet.TCPServer(8080, appserver.NevowSite(NufoxExamples()),
    interface='127.0.0.1')
webServer.setServiceParent(application)

