from twisted.application import internet, service
from nevow import appserver

from twisted.vfs.backends import osfs

from nevow import livepage
from nufox import xul,composite
from twisted.internet.defer import gatherResults, Deferred

from twisted.vfs import ivfs, pathutils

class VFSAgent(object):
    def __init__(self, root):
        self.root = root

    def getChildren(self, segments):
        def _getChildDirs(node):
            return [(name, child)
                for name, child in node.children()
                if not name.startswith(".")
                    and ivfs.IFileSystemContainer.providedBy(child)]

        node = pathutils.fetch(self.root, segments)
        return [(name, len(_getChildDirs(child)) and "false" or "true", [name])
            for name, child in _getChildDirs(node)]

class XULTKPage(xul.XULPage):

    def __init__(self, rootNode):
        self.rootNode = rootNode
        self.pathSegments = []

        self.window = xul.Window(id="xul-window", height=400, width=400,
                                 title="XUL is Cool")

        v = xul.GroupBox(flex=1)
        self.box = v

        v.append(xul.Caption(label="Twisted XUL Sexy Fox Live VFS"))

        b = xul.Button(label="Up")
        b.addHandler('oncommand', self.up)
        v.append(b)

        h = xul.HBox(flex=1)

        self.leftTree = composite.NestedTree(
            VFSAgent(self.rootNode), ["Folders"], flex=1)

        self.leftTree.addHandler("onselect", self.onLeftTreeSelect)

        h.append(self.leftTree)

        h.append(xul.Splitter())

        self.tree = composite.SimpleTree(
            ("Name", "Size", "Type", "Date Modified"),
                enableColumnDrag="true", flex=3)

        self.focus = composite.SequenceSubject()
        self.focus.addObserver(self.tree, self._childToTreeRow)

        self.tree.addHandler('ondblclick', self.treeDblClick)
        h.append(self.tree)
        v.append(h)

        self.window.append(v)

        self.focus.set(
            pathutils.fetch(self.rootNode, self.pathSegments).children())

    def _childToTreeRow(self, item):
        from datetime import datetime
        from twisted.vfs.adapters import web
        import os.path

        name, child = item
        stat = child.getMetadata()
        size = "%s KB" % (stat['size']/1024,)
        mtime = datetime.fromtimestamp(stat['mtime'])

        if ivfs.IFileSystemContainer.providedBy(child):
            mimeType = 'folder'
        else:
            p, ext = os.path.splitext(child.name)
            mimeType = web.loadMimeTypes().get(ext, "text/html")

        return (name, size, mimeType, mtime)

    def updateClient(self):
        self.focus.set(
            pathutils.fetch(self.rootNode, self.pathSegments).children())
        self.leftTree.selectBranch(self.pathSegments)

    def treeDblClick(self):
        def _cbTreeDblClick(result):
            name, child = result[0]
            if ivfs.IFileSystemContainer.providedBy(child):
                self.pathSegments = pathutils.getAbsoluteSegments(
                    self.pathSegments + [name])

                self.updateClient()

        self.tree.getSelection().addBoth(log).addCallback(_cbTreeDblClick)

    def up(self):
        self.pathSegments = self.pathSegments[:-1]
        self.updateClient()

    def onLeftTreeSelect(self, segments):
        self.pathSegments = segments
        self.updateClient()

def log(r):
    print "LOGGING ",r
    return r

root = osfs.OSDirectory(realPath='../..')
application = service.Application('xulvfs')
webServer = internet.TCPServer(8080, appserver.NevowSite(XULTKPage(root)))
webServer.setServiceParent(application)
