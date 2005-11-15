from nufox import xul

style_titre = "text-align:center;color:#000000;font-size:1.5em;\
               font-weight:bold; border:1px dotted #000000;padding:15px;"

L = [['Paul',24,3000],['Albert',45,2500],['Claude',18,4000]]


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
        self.window = xul.Window(height=400, width=400, title="Sorted Columns")
        label = xul.Label(value ="Sorting Columns",style=style_titre)
        grBox = xul.GroupBox(flex=1)
        tree = xul.Tree(
            id="tree",
            flex=1,
            seltpr='single',
            hidecolumnpicker="false",
            )
        s = xul.Splitter(_class = "tree-splitter")
        treecols = xul.TreeCols()
        tname = xul.TreeCol(id = "name", flex = 1, label = "Name")
        tname.addHandler('onclick',self.sortName)
        tage = xul.TreeCol(id = "age", flex = 1, label = "Age")
        tage.addHandler('onclick',self.sortAge)
        tsal = xul.TreeCol(id = "sal", flex = 1, label = "Salary")
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
