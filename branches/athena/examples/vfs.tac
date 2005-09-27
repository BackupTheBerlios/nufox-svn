from twisted.application import internet, service
from nevow import appserver

from twisted.vfs.backends import osfs

from nevow import livepage, rend
from nufox import xul,composite
from twisted.internet.defer import gatherResults, Deferred

from twisted.vfs import ivfs, pathutils

from twisted.vfs import webhack
import twisted.vfs.adapters.stream

from datetime import datetime
from twisted.vfs.adapters import web
import os.path



class VFSAbstraction(object):
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


class CreateFolderDialog(xul.XULPage):
    def __init__(self, parent):
        self.parent = parent

        self.window = xul.Window(id="createFolderDialog",
            onload='document.getElementById("folderName").select();')

        v = xul.VBox(flex=1)
        v.append(xul.DialogHeader(title="Create New Folder"))

        g = xul.GroupBox()
        g.append(xul.Caption(label="Details"))
        h = xul.HBox()
        h.append(xul.Label(value="Folder Name:", align="middle"))
        h.append(xul.TextBox(id="folderName", flex=1, value="new folder"))
        g.append(h)
        v.append(g)

        h = xul.HBox(flex=1, pack="end", align="end")
        b = xul.Button(label="Create", default="true")

        """really unhappy about the window.close as an extra arg getter
        in the handler here"""
        b.addHandler("oncommand", self.parent.createFolder,
            livepage.js("document.getElementById('folderName').value"),
            livepage.js("window.close()"))

        h.append(b)
        b = xul.Button(label="Cancel", oncommand="window.close();")
        h.append(b)
        v.append(h)

        self.window.append(v)



class XULTKPage(xul.XULPage):


    def __init__(self, rootNode):

        self.rootNode = rootNode
        self.pathSegments = []

        self.window = xul.Window(id="xul-window", height=400, width=400,
                                 title="XUL is Cool")

        v = xul.GroupBox(flex=1)
        self.box = v

        v.append(xul.Caption(label="Twisted XUL Sexy Fox Live VFS"))

        h = xul.HBox()
        b = xul.Button(label="Up")
        b.addHandler('oncommand', self.up)
        h.append(b)

        b = xul.Button(label="Create Folder")
        b.addHandler('oncommand', self.fireCreateFolderDialog)
        h.append(b)
        v.append(h)

        h = xul.HBox(flex=1)

        self.leftTree = composite.NestedTree(
            VFSAbstraction(self.rootNode), ["Folders"], flex=1)

        self.leftTree.addHandler("onselect", self.onLeftTreeSelect)

        h.append(self.leftTree)

        h.append(xul.Splitter())

        self.rightTree = composite.SimpleTree(
            ("Name", "Size", "Type", "Date Modified"),
                enableColumnDrag="true", flex=3)

        self.focus = composite.SequenceSubject()
        self.focus.addObserver(self.rightTree, self._childToTreeRow)

        self.rightTree.addHandler('ondblclick', self.onRightTreeDblClick)
        h.append(self.rightTree)
        v.append(h)

        self.window.append(v)

        self.setRightTreeFocus()

    def _childToTreeRow(self, item):

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

    def setRightTreeFocus(self):
        self.focus.set([(name, child) for name, child in
                pathutils.fetch(self.rootNode, self.pathSegments).children()
                if not name.startswith(".")])

    def onRightTreeDblClick(self, result):
        name, child = result
        if ivfs.IFileSystemContainer.providedBy(child):
            self.pathSegments = pathutils.getAbsoluteSegments(
                self.pathSegments + [name])
            self.setRightTreeFocus()
            self.leftTree.selectBranch(self.pathSegments)
        else:
            self.client.send(
                livepage.js.window.open(
                    "files/%s" % "/".join(self.pathSegments + [name]),
                    "openfile"))

    def up(self):
        self.pathSegments = self.pathSegments[:-1]
        self.setRightTreeFocus()
        self.leftTree.selectBranch(self.pathSegments)

    def onLeftTreeSelect(self, segments):
        self.pathSegments = segments
        self.setRightTreeFocus()

    def locateChild(self, context, segments):
        if segments[0] == "files":
            node = pathutils.fetch(self.rootNode, list(segments[1:]))
            p, ext = os.path.splitext(node.name)
            return webhack.Stream(node, web.loadMimeTypes().get(
                ext, "text/html")), ()

        return xul.XULPage.locateChild(self, context, segments)

    def childFactory(self, context, name):
        if name == "createFolder":
            return CreateFolderDialog(self)

    def fireCreateFolderDialog(self):
        self.client.send(livepage.js.window.open(
                "createFolder", "createFolderDialog",
                    "width=400,height=150,dialog"))

    def createFolder(self, folderName, close):
        node = pathutils.fetch(self.rootNode, self.pathSegments)
        child = node.createDirectory(folderName)
        self.focus.append((folderName, child))

        """XXX - this isn't right at all, still working out how to do it"""
        self.leftTree.reloadBranch(self.pathSegments)

def log(r):
    print "LOGGING ",r
    return r

root = osfs.OSDirectory(realPath='../..')
application = service.Application('xulvfs')
webServer = internet.TCPServer(8080, appserver.NevowSite(XULTKPage(root)))
webServer.setServiceParent(application)
