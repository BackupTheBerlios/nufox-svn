from nufox import xul
from nufox.xul import htmlns as H


class Example(xul.XULPage):
    """Embed HTML

    This example shows how you can embed conventional HTML into XUL."""

    def setup(self):
        self.window = xul.Window(id=u"xul-window", height=400, width=400,
                                 title=u"Press this button!")
        v = xul.VBox(flex=2)
        v.append(H.h1[u"This is an H1 tag, embedded in XUL."])
        v.append(
            H.table(border=1, width=u'50%')[
                H.colgroup[
                    H.col(width=u'50%'),
                    H.col(width=u'50%')
                ],
                H.tr[
                    H.th(colspan=2)[u"An HTML Table"]
                ],
                H.tr[
                    H.td[u"Wallaby"],
                    H.td[u"Bilby"]
                ],
                H.tr[
                    H.td[u"Echidna"],
                    H.td[u"Possum"]
                ]

            ]
        )
        self.window.append(v)

