from twisted.application import internet, service
from nevow import appserver

from twisted.vfs.backends import osfs

from nevow import livepage
from nufox import xul,composite
from twisted.internet.defer import gatherResults, Deferred

from twisted.vfs import ivfs, pathutils

class NodeState(object):
    def __init__(self, xulnode, vfsnode, opened, subtree={}):
        self.xulnode = xulnode
        self.vfsnode = vfsnode
        self.opened = opened
        self.subtree = subtree

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

        t = xul.Tree(flex=1, seltype="single")
        th = xul.TreeCols()
        th.append(xul.TreeCol(flex=1, label="Folders", primary="true"))
        t.append(th)

        self.inview = NodeState(t, self.rootNode, True)

        self.idToNodeState = {}

        tc = xul.TreeChildren()

        for name, node in self.rootNode.children():
            if not name.startswith('.'):
                if ivfs.IFileSystemContainer.providedBy(node):
                    ti = xul.TreeItem(container="true", open="false",
                        empty=len([n for n, c in node.children()
                                if not n.startswith('.') and
                                ivfs.IFileSystemContainer.providedBy(c)])
                            and "false" or "true")

                    tr = xul.TreeRow()
                    tr.append(xul.TreeCell(label=name))
                    ti.append(tr)
                    tc.append(ti)

                    self.inview.subtree[name] = NodeState(ti, node, False)
                    self.idToNodeState[str(ti.id)] = self.inview.subtree[name]

        t.append(tc)
        h.append(t)

        t.addHandler('onselect', self.bork)
        self.leftTree = t

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

        self.updateClient()

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
        self.openBranch()

    def _fetchNodeState(self):
        nodestate = self.inview
        for segment in self.pathSegments:
            nodestate = nodestate.subtree[segment]
        return nodestate

    def openBranch(self):
        if len(self.pathSegments):

            nodestate = self._fetchNodeState()

            if not nodestate.opened:

                children = [
                    (name, node) for name, node in nodestate.vfsnode.children()
                        if not name.startswith('.') and
                        ivfs.IFileSystemContainer.providedBy(node)]

                if len(children):
                    tc = xul.TreeChildren()
                    for name, node in children:
                        if not name.startswith('.'):
                            if ivfs.IFileSystemContainer.providedBy(node):
                                ti = xul.TreeItem(container="true", open="false",
                                    empty=len([n for n, c in node.children()
                                            if not n.startswith('.') and
                                            ivfs.IFileSystemContainer.providedBy(c)])
                                        and "false" or "true")
                                tr = xul.TreeRow()
                                tr.append(xul.TreeCell(label=name))
                                ti.append(tr)
                                tc.append(ti)

                                nodestate.subtree[name] = NodeState(ti, node, False)
                                self.idToNodeState[str(ti.id)] = nodestate.subtree[name]

                    nodestate.xulnode.append(tc)
                    nodestate.xulnode.setAttr("open", "true")
                nodestate.opened = True

    def treeDblClick(self):
        def _cbTreeDblClick(result):
            name, child = result[0]
            if ivfs.IFileSystemContainer.providedBy(child):
                self.pathSegments = pathutils.getAbsoluteSegments(
                    self.pathSegments + [name])

                self.leftTree.pageCtx.client.send(livepage.js.TreeSetSelected(
                    self.leftTree.id, self._fetchNodeState().xulnode.id))

                self.updateClient()

        self.tree.getSelection().addBoth(log).addCallback(_cbTreeDblClick)

    def up(self):
        self.pathSegments = self.pathSegments[:-1]
        self.updateClient()

    def bork(self):
        def _cbBork(result):
            print "ORAOROROR!!!"
            nodestate = self.idToNodeState[result]
            segments = pathutils.getSegments(nodestate.vfsnode)
            print segments
            print segments == self.pathSegments
            if segments != self.pathSegments:
                print "NENENENENEN"
                self.pathSegments = segments
                self.updateClient()


        d = Deferred()
        getter = self.leftTree.pageCtx.client.transient(lambda ctx, r: d.callback(r))
        self.leftTree.pageCtx.client.send(getter(livepage.js.TreeGetSelected(
            self.leftTree.id)))
        d.addCallback(_cbBork)


def log(r):
    print "LOGGING ",r
    return r

root = osfs.OSDirectory(realPath='../..')
application = service.Application('xulvfs')
webServer = internet.TCPServer(8080, appserver.NevowSite(XULTKPage(root)))
webServer.setServiceParent(application)
