from nufox import xul

class Calculator(xul.XULPage):

    def __init__(self):
        self.window = xul.Window(id="xul=window", height=400, width=400,
        title="Calculator")
        v = xul.VBox(flex=1)
        for i in range(10):
            buttonId = 'button%s'%(i,)
            setattr(self, buttonId, xul.Button(id=buttonId, label=i))
        self.plus = xul.Button(id='plus', label='+', flex=1)
        self.minus = xul.Button(id='minus', label='-', flex=1)
        self.times = xul.Button(id='times', label='x', flex=1)
        self.display = xul.TextBox(id='display', readonly='true',value=0,flex=1)
        row1 = xul.HBox(flex=1)
        row1.append(self.button1)
        row1.append(self.button2)
        row1.append(self.button3)
        row1.append(self.minus)
        row2 = xul.HBox(flex=1)
        row2.append(self.button4)
        row2.append(self.button5)
        row2.append(self.button6)
        row2.append(self.plus)
        row3 = xul.HBox(flex=1)
        row3.append(self.button7)
        row3.append(self.button8)
        row3.append(self.button9)
        row3.append(self.times)
        row4 = xul.HBox(flex=1)
        row4.append(self.button0)
        v.append(self.display)
        v.append(row1)
        v.append(row2)
        v.append(row3)
        v.append(row4)
        self.window.append(v)

    def reset(self):
        self.display.setAttr(self.client, 'value', 0)
example = Calculator()
