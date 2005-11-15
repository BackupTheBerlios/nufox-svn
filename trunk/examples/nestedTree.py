"""Contributed by Lukeg"""

import os
from stat import *
import sys

from nufox import deploy
from nufox import xul


class Example(xul.XULPage):
    """Nested Tree"""

    discussion = """
    Contributed by Lukeg.
    """

    def setup(self):
        self.window = xul.Window()
        self.vbox = xul.VBox()
        self.tree = xul.Tree(flex=1, rows=10)
        self.tree.addHandler(
            'onselect', self.click_row, self.tree.requestAttr('currentIndex'))
        self.colonnes = xul.TreeCols(flex=1)
        self.cols_name = {
            'Fichier': None,
            'path': None,
            'size': None,
            }
        self.cols_order = [
            'Fichier',
            'path',
            'size',
            ]
        for col in self.cols_order:
            if col == self.cols_order[0]:
                my_col = xul.TreeCol(label=col, flex=1, primary='true')
            else:
                my_col = xul.TreeCol(label=col, flex=1)
            self.cols_name[col] = my_col
            self.colonnes.append(my_col)
            self.colonnes.append(xul.TreeSeparator().append(xul.Grippy()))
        self.tree_children = xul.TreeChildren()
        self.fichiers_infos = self.walktree(os.getcwd())
        for fich in self.fichiers_infos[1]:
           file_item = self.create_tree_item(fich)
           self.tree_children.append(file_item)
        self.tree.append(self.colonnes)
        self.tree.append(self.tree_children)
        self.vbox.append(xul.GroupBox().append(self.tree))
        self.label = xul.Label(value='no information')
        self.caption= xul.Caption(label='File informations')
        self.vbox.append(xul.GroupBox().append(self.caption, self.label))
        self.window.append(self.vbox)

    def walktree(self, top):
        """
        recursively descend the directory tree rooted at top
        Some comments about the data structures:
          returns a tuple (directory name, [list of files and sub directories])
          a file is a tuple: (filename, file path, size)
            e.g : ('foo', '/tmp/foo', '200 b')
          a sub directory is a tuple like the directory one
          (dir name, [list of files])
            example: ('tmp', [('foo', '/tmp/foo', '200b'),
                      ('dir', ['foo2','/tmp/dir/foo2', '300b']))
            /tmp:
            |__  foo
            |__  dir:
                 |__ foo2
        """

        res = []
        for f in os.listdir(top):
            pathname = os.path.join(top, f)
            my_stat = os.stat(pathname)
            mode = my_stat[ST_MODE]
            size = my_stat[ST_SIZE]
            if S_ISDIR(mode):
                # It's a directory, recurse into it
                #walktree(pathname)
                files = self.walktree(pathname)
                res.append(files)
            elif S_ISREG(mode):
                # It's a file
                size = int(size)
                if size < 1024:
                    t = ' b'
                elif size < (1024*1024):
                    t = ' Kb'
                    size /= 1024
                else :
                    t = ' Mb'
                    size /= 1024*1024
                res.append((f, pathname, str(size)+t))
            else:
                # Unknown file type, print a message
                print 'Skipping %s' % pathname
        res.sort()
        dir = os.path.basename(os.path.abspath(top))
        return (dir, res)

    def click_row(self, index):
        if index != -1:
            defer = self.callRemote('TreeGetSelected', self.tree.id)
            defer.addCallback(self.print_cell_text)

    def print_cell_text(self, row):
        def _change_text(txt):
            filepath = txt[0][0]
            if filepath == '':
                txt = 'Directory'
            else:
                cmd = 'file '+filepath
                fd = os.popen2(cmd)
                txt = fd[1].read().strip()
            self.label.setAttr('value',unicode(txt))
        defer = self.callRemote('GetCellText', row[0][0][0], 1)
        defer.addCallback(_change_text)

    def create_tree_item(self, file_list):
        tree_row = xul.TreeRow(flex=1)
        # It's a file
        if len(file_list) == 3:
            item = xul.TreeItem()
            cell = xul.TreeCell(label=file_list[0])
            cell2 = xul.TreeCell(label=file_list[1])
            cell3 = xul.TreeCell(label=file_list[2])
            tree_row.append(cell, cell2, cell3)
            item.append(tree_row)
        # It's a directory
        else:
            item = xul.TreeItem(container='true')
            cell = xul.TreeCell(label=file_list[0])
            cell2 = xul.TreeCell(label='')
            cell3 =  xul.TreeCell(label='')
            child = xul.TreeChildren()
            for i in file_list[1]:
                my_item = self.create_tree_item(i)
                child.append(my_item)
            tree_row.append(cell, cell2, cell3)
            item.append(tree_row)
            item.append(child)
        return item
