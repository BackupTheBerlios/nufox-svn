from py.test import raises

from nufox.widget._dispatcher.robustapply import *


def noArgument():
    pass


def oneArgument(blah):
    pass


def twoArgument(blah, other):
    pass


class TestRobustApply(object):
    
    def test_01(self):
        robustApply(noArgument)
        
    def test_02(self):
        raises(TypeError, robustApply, noArgument, 'this' )
        
    def test_03(self):
        raises(TypeError, robustApply, oneArgument)
        
    def test_04(self):
        """Raise error on duplication of a particular argument"""
        raises(TypeError, robustApply, oneArgument, 'this', blah='that')

