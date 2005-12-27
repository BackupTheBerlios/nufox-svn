from nufox import xul

style_titre = u"text-align:center;color:#000000;font-size:1.5em;\
               font-weight:bold; border:1px dotted #000000;padding:15px;"

L = [[u'Paul',24,3000],[u'Albert',45,2500],[u'Claude',18,4000]]


def sortLists(listes,critere=0):
    d = {}
    for liste in listes:
        d[liste[critere]] = liste
    cles = sorted(d.keys())
    #Thanks Alex Martelli
    return map(d.get,cles)


class Example(xul.XULPage):
    """Sorted Columns"""

    discussion = """
    Contributed by Salvatore Didio.
    """
    
    def setup(self):
        self.window = xul.Window(height=400, width=400,
                                 title=u"Sorted Columns")
        label = xul.Label(value =u"Sorting Columns",style=style_titre)
        grBox = xul.GroupBox(flex=1)
        tree = xul.Tree(
            id=u"tree",
            flex=1,
            seltpr=u'single',
            hidecolumnpicker=u"false",
            )
        s = xul.Splitter(_class = u"tree-splitter")
        treecols = xul.TreeCols()
        tname = xul.TreeCol(id = u"name", flex = 1, label = u"Name")
        tname.addHandler('onclick',self.sortName)
        tage = xul.TreeCol(id = u"age", flex = 1, label = u"Age")
        tage.addHandler('onclick',self.sortAge)
        tsal = xul.TreeCol(id = u"sal", flex = 1, label = u"Salary")
        tsal.addHandler('onclick',self.sortSalary)
        treecols.append(tname,s,tage,s,tsal)
        self.treechild = xul.TreeChildren()
        self.displayData(L)
        tree.append(treecols,self.treechild)
        grBox.append(tree)
        self.window.append(label,grBox)

    def displayData(self,l):
        self.treechild.clear()
        for i in range(len(l)):
                itemnum = xul.TreeItem()
                rownum = xul.TreeRow()
                itemnum.append(rownum)
                rownum.append(xul.TreeCell(label = unicode(l[i][0])))
                rownum.append(xul.TreeCell(label = unicode(l[i][1])))
                rownum.append(xul.TreeCell(label = unicode(l[i][2])))
                self.treechild.liveAppend(itemnum)

    def sortName(self):
        self.displayData(sortLists(L,0))

    def sortAge(self):
        self.displayData(sortLists(L,1))

    def sortSalary(self):
        self.displayData(sortLists(L,2))
