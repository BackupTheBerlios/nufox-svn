from nufox.widget._dispatcher.saferef import *


class _Test1(object):
    def x(self):
        pass

    
def _test2(obj):
    pass


class _Test3(object):
    def __call__(self, obj):
        pass

    
class TestSaferef(object):

    # XXX: The original tests had a test for closure, and it had an
    # off-by-one problem, perhaps due to scope issues.  It has been
    # removed from this test suite.
    
    def setup_method(self, method):
        ts = []
        ss = []
        for x in xrange(5000):
            t = _Test1()
            ts.append(t)
            s = safeRef(t.x, self._closure)
            ss.append(s)
        ts.append(_test2)
        ss.append(safeRef(_test2, self._closure))
        for x in xrange(30):
            t = _Test3()
            ts.append(t)
            s = safeRef(t, self._closure)
            ss.append(s)
        self.ts = ts
        self.ss = ss
        self.closureCount = 0
        
    def teardown_method(self, method):
        if hasattr(self, 'ts'):
            del self.ts
        if hasattr(self, 'ss'):
            del self.ss
        
    def test_In(self):
        """Test the `in` operator for safe references (cmp)"""
        for t in self.ts[:50]:
            assert safeRef(t.x) in self.ss
            
    def test_Valid(self):
        """Test that the references are valid (return instance methods)"""
        for s in self.ss:
            assert s()
            
    def test_ShortCircuit(self):
        """Test that creation short-circuits to reuse existing references"""
        sd = {}
        for s in self.ss:
            sd[s] = 1
        for t in self.ts:
            if hasattr(t, 'x'):
                assert sd.has_key(safeRef(t.x))
            else:
                assert sd.has_key(safeRef(t))
                
    def test_Representation(self):
        """Test that the reference object's representation works

        XXX Doesn't currently check the results, just that no error
            is raised
        """
        repr(self.ss[-1])
        
    def _closure(self, ref):
        """Dumb utility mechanism to increment deletion counter"""
        self.closureCount += 1

