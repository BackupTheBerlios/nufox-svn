from nevow import static

from twisted.python.util import sibpath

from nufox import xul


class Example(xul.XULPage):
    """XML Periodic Table: Box Layout"""

    discussion = """
    Based on http://www.hevanet.com/acorbin/xul/top.xul
    """

    child_images = static.File(sibpath(__file__, 'xptImages'))

    def setup(self):
        window = self.window = xul.Window()
        vbox = xul.VBox(flex=1, style=u'overflow: auto')
        window.append(vbox)
        # Flexiness.
        groupbox = xul.GroupBox().append(xul.Caption(label=u'Flexiness'))
        vbox.append(groupbox)
        groupbox.append(xul.HBox().append(
            xul.Button(label=u'No Flex'),
            xul.Button(label=u'No Flex'),
            xul.Button(label=u'No Flex'),
            xul.Button(label=u'No Flex'),
            xul.Button(label=u'No Flex'),
            ))
        groupbox.append(xul.HBox().append(
            xul.Button(label=u"There's a"),
            xul.Button(label=u'spacer'),
            xul.Spacer(flex=1),
            xul.Button(label=u'in the'),
            xul.Button(label=u'middle.'),
            ))
        groupbox.append(xul.HBox().append(
            xul.Button(label=u'This spacer ->'),
            xul.Spacer(flex=2),
            xul.Button(label=u'is bigger than this spacer, ->'),
            xul.Spacer(flex=1),
            xul.Button(label=u'so there!'),
            ))
        groupbox.append(xul.HBox().append(
            xul.Button(label=u'No Flex'),
            xul.Button(label=u'No Flex'),
            xul.Button(flex=1, label=u'flex=1'),
            xul.Button(label=u'No Flex'),
            xul.Button(label=u'No Flex'),
            ))
        groupbox.append(xul.HBox().append(
            xul.Button(flex=1, label=u'flex=1'),
            xul.Button(flex=2, label=u'flex=2'),
            xul.Button(flex=3, label=u'flex=3'),
            xul.Button(flex=4, label=u'flex=4'),
            xul.Button(flex=5, label=u'flex=5'),
            ))
        groupbox.append(xul.HBox().append(
            xul.Button(flex=1, label=u'flex=1'),
            xul.Button(flex=1, label=u'flex=1'),
            xul.Button(flex=1, label=u'flex=1'),
            xul.Button(flex=1, label=u'flex=1'),
            xul.Button(flex=1, label=u'flex=1'),
            ))
        # Direction.
        groupbox = xul.GroupBox().append(xul.Caption(label=u'Direction'))
        vbox.append(groupbox)
        for direction in [u'forward', u'reverse']:
            groupbox.append(xul.HBox(dir=direction).append(
                xul.Button(label=u'Here'),
                xul.Button(label=u'the'),
                xul.Button(label=u'direction'),
                xul.Button(label=u'is'),
                xul.Button(label=direction),
                ))
        groupbox.append(xul.HBox().append(
            xul.Button(label=u'Here the', ordinal=4),
            xul.Button(label=u'ordinal', ordinal=1),
            xul.Button(label=u'attribute', ordinal=3),
            xul.Button(label=u'sets the order.', ordinal=2),
            ))
        # Packing.
        groupbox = xul.GroupBox().append(xul.Caption(label=u'Packing'))
        vbox.append(groupbox)
        for pack in [u'start', u'center', u'end']:
            groupbox.append(xul.HBox(pack=pack).append(
                xul.Button(label=u'Here'),
                xul.Button(label=u'the'),
                xul.Button(label=u'packing'),
                xul.Button(label=u'is'),
                xul.Button(label=pack),
                ))
        groupbox.append(xul.HBox(pack=u'start').append(
            xul.Button(label=u'Here'),
            xul.Button(label=u'packing'),
            xul.Button(label=u'yields'),
            xul.Button(label=u'to'),
            xul.Button(label=u'flex', flex=1),
            ))
        # Alignment.
        groupbox = xul.GroupBox().append(xul.Caption(label=u'Alignment'))
        vbox.append(groupbox)
        for align in [u'start', u'center', u'end', u'baseline', u'stretch']:
            groupbox.append(xul.HBox(align=align).append(
                xul.Button(label=u'Here',
                           image='images/betty_boop.xbm',
                           orient='vertical'
                           ),
                xul.Button(orient='vertical',
                           ).append(xul.Label(value=u'the'),
                                    xul.Label(value=u'alignment')),
                xul.Button(label=u'is', image='images/betty_boop.xbm'),
                xul.Button(label=align),
                ))
        # Equality.
        groupbox = xul.GroupBox().append(xul.Caption(label=u'Equality'))
        vbox.append(groupbox)
        hbox = xul.HBox()
        groupbox.append(hbox)
        for equalsize in [u'always', u'never']:
            hbox.append(xul.VBox(equalsize=equalsize).append(
                xul.Button(label=u'Here',
                           image='images/betty_boop.xbm',
                           orient=u'vertical'
                           ),
                xul.Button(orient=u'vertical',
                           ).append(xul.Label(value=u'the'),
                                    xul.Label(value=u'equalsize'),
                                    xul.Label(value=u'attribute')),
                xul.Button(label=u'is', image='images/betty_boop.xbm'),
                xul.Button(label=equalsize),
                ))
        # Hiddenness.
        groupbox = xul.GroupBox().append(xul.Caption(label=u'Hiddenness'))
        vbox.append(groupbox)
        groupbox.append(xul.HBox().append(xul.Label(
            value=u'Every other button in the line below is hidden.')))
        groupbox.append(xul.HBox().append(
            xul.Button(label=u'Every'),
            xul.Button(label=u'other', hidden=u'true'),
            xul.Button(label=u'button'),
            xul.Button(label=u'in', hidden=u'true'),
            xul.Button(label=u'the'),
            xul.Button(label=u'line', hidden=u'true'),
            xul.Button(label=u'below'),
            xul.Button(label=u'is', hidden=u'true'),
            xul.Button(label=u'hidden'),
            ))
