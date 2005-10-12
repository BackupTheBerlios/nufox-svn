from nufox import xul
from nufox.xul import htmlns as H

class Example(xul.XULPage):
    """This example shows how you can embed conventional HTML into XUL."""
    def setup(self):
        self.window = xul.Window(id="xul-window", height=400, width=400,
                                 title="Press this button!")
        v = xul.VBox(flex=2)
        v.append(H.h1["This is an H1 tag, embedded in XUL."])
        v.append(
            H.table(border=1, width='50%')[
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

