from nevow import livepage
from nufox import xul
from nufox.xul import htmlns as H

class XULTKPage(xul.XULPage):

    def __init__(self):
        self.window = xul.Window(id="xul-window", height=400, width=400,
                                 title="Press this button!")
        v = xul.VBox(flex=2)
        b = xul.Button(id='sendCrap', label="A Button")
        v.append(b)
        v.append(H.h1["This is an H1 tag"])
        v.append(
            H.table(border=1)[
                H.colgroup[
                    H.col(width='50%'),
                    H.col(width='50%')
                ],
                H.tr[
                    H.th(colspan=2)["An HTML Table"]
                ],
                H.tr[
                    H.td["Wallaby"],
                    H.td["Bilby"]
                ],
                H.tr[
                    H.td["Echidna"],
                    H.td["Possum"]
                ]

            ]
        )
        self.window.append(v)

example = XULTKPage()
