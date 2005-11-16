"""PyDispatcher plugin tests."""

from py.test import skip

from nufox.widget._dispatcher import dispatcher
from nufox.widget._dispatcher.plugin import QtWidget

try:
    import qt
    if not hasattr(qt.qApp, 'for_testing'):
        _app = qt.QApplication([])
        _app.for_testing = True
        qt.qApp = _app
except ImportError:
    qt = None


class ReceiverBase(object):

    def __init__(self):
        self.args = []
        self.live = True

    def __call__(self, arg):
        self.args.append(arg)

class Receiver1(ReceiverBase):
    pass

class Receiver2(ReceiverBase):
    pass


class Plugin1(dispatcher.Plugin):

    def is_live(self, receiver):
        """ReceiverBase instances are only live if their `live`
        attribute is True"""
        if isinstance(receiver, ReceiverBase):
            return receiver.live
        return True


class Plugin2(dispatcher.Plugin):

    def is_live(self, receiver):
        """Pretend all Receiver2 instances are not live."""
        if isinstance(receiver, Receiver2):
            return False
        return True


def test_is_live():
    dispatcher.reset()
    # Create receivers.
    receiver1a = Receiver1()
    receiver1b = Receiver1()
    receiver2a = Receiver2()
    receiver2b = Receiver2()
    # Connect signals.
    dispatcher.connect(receiver1a, 'sig')
    dispatcher.connect(receiver1b, 'sig')
    dispatcher.connect(receiver2a, 'sig')
    dispatcher.connect(receiver2b, 'sig')
    # Check reception without plugins.
    dispatcher.send('sig', arg='foo')
    assert receiver1a.args == ['foo']
    assert receiver1b.args == ['foo']
    assert receiver2a.args == ['foo']
    assert receiver2b.args == ['foo']
    # Install plugin 1.
    plugin1 = Plugin1()
    dispatcher.plugins.append(plugin1)
    # Make some receivers not live.
    receiver1a.live = False
    receiver2b.live = False
    # Check reception.
    dispatcher.send('sig', arg='bar')
    assert receiver1a.args == ['foo']
    assert receiver1b.args == ['foo', 'bar']
    assert receiver2a.args == ['foo', 'bar']
    assert receiver2b.args == ['foo']
    # Remove plugin 1, install plugin 2.
    plugin2 = Plugin2()
    dispatcher.plugins.remove(plugin1)
    dispatcher.plugins.append(plugin2)
    # Check reception.
    dispatcher.send('sig', arg='baz')
    assert receiver1a.args == ['foo', 'baz']
    assert receiver1b.args == ['foo', 'bar', 'baz']
    assert receiver2a.args == ['foo', 'bar']
    assert receiver2b.args == ['foo']
    # Install plugin 1 alongside plugin 2.
    dispatcher.plugins.append(plugin1)
    # Check reception.
    dispatcher.send('sig', arg='fob')
    assert receiver1a.args == ['foo', 'baz']
    assert receiver1b.args == ['foo', 'bar', 'baz', 'fob']
    assert receiver2a.args == ['foo', 'bar']
    assert receiver2b.args == ['foo']
    

def test_qt_plugin():
    if qt is None:
        skip('PyQt not installed.')
    dispatcher.reset()
    # Create receivers.
    class Receiver(qt.QWidget):
        def __init__(self):
            qt.QObject.__init__(self)
            self.args = []
        def receive(self, arg):
            self.args.append(arg)
    receiver1 = Receiver()
    receiver2 = Receiver()
    # Connect signals.
    dispatcher.connect(receiver1.receive, 'sig')
    dispatcher.connect(receiver2.receive, 'sig')
    # Destroy receiver2 so only a shell is left.
    receiver2.close(True)
    # Check reception without plugins.
    dispatcher.send('sig', arg='foo')
    assert receiver1.args == ['foo']
    assert receiver2.args == ['foo']
    # Install plugin.
    plugin = QtWidget()
    dispatcher.plugins.append(plugin)
    # Check reception with plugins.
    dispatcher.send('sig', arg='bar')
    assert receiver1.args == ['foo', 'bar']
    assert receiver2.args == ['foo']

