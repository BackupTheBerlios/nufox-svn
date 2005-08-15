from nevow import livepage
from nufox import xul

class XULTKPage(xul.XULPage):

    def __init__(self):
        self.counter = 0
        self.window = xul.Window(id="xul-window", height=400, width=400,
                                 title="XUL is Cool")
        v = xul.GroupBox(flex=1)
        v.append(xul.Caption(label="Fun"))

        def listToListBox(list, haveHeader=False):
            lb = xul.ListBox(rows=len(list))
            if not len(list): return lb

            if not isinstance(list[0], type(())):
                list = [(item,) for item in list]

            lc = xul.ListCols()
            for i in range(len(list[0])):
                lc.append(xul.ListCol())
            lb.append(lc)

            if haveHeader:
                header = list[0]
                list = list[1:]
                lh = xul.ListHead()
                for cell in header:
                    lh.append(xul.ListHeader(label=cell))
                lb.append(lh)

            for row in list:
                li = xul.ListItem(value=row[0])
                for cell in row:
                    li.append(xul.ListCell(label=cell))
                lb.append(li)
            return lb

        lb = listToListBox([("Name", "Age"),
            ("ned", 23),
            ("fred", 35),
            ("ted", 52),], haveHeader=True)

        lb.addHandler('onselect', self.listSelect)
        self.listBox = lb
        v.append(lb)

        self.window.append(v)

    def listSelect(self):
        d = self.listBox.getAttr(self.client, 'value')
        d.addBoth(log)

def log(r):
    print "LOGGING ",r
    return r

example = XULTKPage()
