"""XUL-based unit test support."""

from twisted.internet import reactor
from twisted.trial import unittest

from nufox import xul


class TestRunner(xul.XULPage):

    addSlash = True
    testRunning = False
    nextTest = False
    
    def __init__(self, testsToRun):
        self.testsToRun = testsToRun
        self.window = xul.Window(title="Nufox Unit Tester")
        self.output = xul.VBox(flex=1)
        self.scratch = xul.IFrame(flex=1)
        vbox = xul.VBox(flex=1)
        button = xul.Button(label="Run Tests")
        button.addHandler('oncommand', self.runAll)
        outputbox = xul.GroupBox(flex=80, style='overflow:auto;')
        outputbox.append(xul.Caption(label='Test Output'))
        scratchbox = xul.GroupBox(flex=20)
        scratchbox.append(xul.Caption(label='Test Scratch Frame'))
        outputbox.append(self.output)
        scratchbox.append(self.scratch)
        vbox.append(button, outputbox, scratchbox)
        self.window.append(vbox)
        

    def runAll(self):
        print "RUNALL!!!!!!!!!!!!!!!!!!!!!!"
        for klass in self.testsToRun:
            self.setupTestPage(klass)
            print dir(klass)
            for attr in dir(klass):
                #if callable(getattr(klass,attr)) and attr.startswith('test_'):
                if attr.startswith('test_'):
                    print "FOUND TEST", attr
                    self.scratch.setAttr('src', 'test')
                    self.nextTest = attr
            
    def setupTestPage(self, klass):
        print "SETTING UP ", klass
        self.currentTestClass = klass

    def childFactory(self, ctx, name):
        if not hasattr(self, 'currentActiveTest'):
            print "##############FIRST TIME IN"
            self.currentActiveTest = self.currentTestClass()
            self.testRunning = True
            self.runTest(self.nextTest)
            return self.currentActiveTest
        else:
            print "###############NOT FIRST TIME IN"
            return self.currentActiveTest
            
    def runTest(self, test):
        print "RUNNING TEST", test
        try:
            getattr(self.currentActiveTest, test)()
        except Exception, e:
            self.handleException(e)
        self.currentActiveTest.tearDown()
        self.testRunning = False

    def handleException(self, e):
        """I update the UI with the exception"""
        print "HANDLING EXCEPTION!"
        self.output.append(xul.Label(value=e))
        

class XULTest(xul.XULPage, unittest.TestCase):

    def __init__(self):
        self.window = xul.Window()
        self.setUp()
        
    
