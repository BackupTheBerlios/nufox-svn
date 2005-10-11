import operator
from nufox import xul

class Example(xul.XULPage):

    def setup(self):
        self.currentValue = 0
        self.LHS = 0 #for keeping LHS of equasions
        self.equasion = None #what is the current equasion we're evaluating?
        self.window = xul.Window(height=400, width=400, title="Calculator")
        v = xul.VBox(flex=1)
        self.keyset = xul.KeySet() #setup keys :)
        #make some buttons
        for i in range(10):
            buttonId = 'button%s'%(i,)
            setattr(self, buttonId, xul.Button(id=buttonId, label=i))
            button = getattr(self, buttonId)
            button.addHandler('oncommand', 
                lambda num=i, *js: self.numberPressed(num, *js))
            #add a numpad keybinding for this button
            keystroke = xul.Key(keycode="VK_NUMPAD%s" % (i,))
            keystroke.addHandler('oncommand',
                lambda num=i, *js: self.numberPressed(num, *js))
            self.keyset.append(keystroke)
        #add some buttons with handlers for + - * = and C
        self.equals = xul.Button(id='equals', label='=', flex=1)
        self.equals.addHandler('oncommand', self.equalsPressed)
        self.clear = xul.Button(id='clear', label='C', flex=1)
        self.clear.addHandler('oncommand', self.clearPressed)
        self.plus = xul.Button(id='plus', label='+', flex=1)
        self.plus.addHandler('oncommand', self.plusPressed)
        self.minus = xul.Button(id='minus', label='-', flex=1)
        self.minus.addHandler('oncommand', self.minusPressed)
        self.times = xul.Button(id='times', label='x', flex=1)
        self.times.addHandler('oncommand', self.timesPressed)
        #lay it all out
        self.display = xul.TextBox(id='display', rows=1, 
            readonly='true',value=0,flex=1)
        row1 = xul.HBox(flex=1)
        row1.append(self.button1, self.button2, self.button3, self.minus)
        row2 = xul.HBox(flex=1)
        row2.append(self.button4, self.button5, self.button6, self.plus)
        row3 = xul.HBox(flex=1)
        row3.append(self.button7, self.button8, self.button9, self.times)
        row4 = xul.HBox(flex=1)
        row4.append(self.button0, self.clear, self.equals)
        v.append(self.display)
        v.append(row1, row2, row3, row4)
        self.window.append(self.keyset)
        self.window.append(v)


    def updateDisplay(self, value):
        self.currentValue = value
        self.display.setAttr('value', value)

    def numberPressed(self, num):
        if int(self.currentValue) == 0:
            val = num
        else:
            val = '%s%s'%(self.currentValue, num)
        self.updateDisplay(val) 
         
    def clearPressed(self):
        self.LHS = 0
        self.updateDisplay(0)

    def equalsPressed(self):
        val = self.equasion(int(self.LHS), int(self.currentValue))
        self.LHS = 0
        self.equasion = None
        self.updateDisplay(val)
        
    def plusPressed(self):
        self.equasion = operator.add 
        self.LHS = self.currentValue
        self.updateDisplay(0)
        
    def minusPressed(self):
        self.equasion = operator.sub 
        self.LHS = self.currentValue
        self.updateDisplay(0)

    def timesPressed(self):
        self.equasion = operator.mul 
        self.LHS = self.currentValue
        self.updateDisplay(0)
