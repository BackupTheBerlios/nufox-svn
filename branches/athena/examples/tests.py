from nufox import xultrial, xul
from twisted.trial import assertions as A

class Example(xultrial.XULTest):

    def setUp(self):
        print "RUNNING MYTEST SETUP"
        self.label = xul.Label(value="0")
        self.window.append(self.label)

    def test_setAttr(self):
        print "RUNNING TEST 1"
        self.label.setAttr('value', 1)
        a.fail()

    def test_foo(self):
        print "RUNNING TEST 2"
        self.label.setAttr('value', 'foo')

#example = xultrial.TestRunner([MyTest])
