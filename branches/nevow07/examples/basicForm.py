from nufox import xul, xulform


class Example(xul.XULPage):
    """Basic Form (debug me)

    Shows how the nufox.xulform.FieldAggregate class can be used to
    simplify submitting multiple fields with a single submit."""
    
    def setup(self):
        self.window = xul.Window(title=u"Forms Test")
        #A place to display our form results
        self.display = xul.Label()

        #three fields:
        firstname = xul.TextBox(id=u"firstname")
        surname = xul.TextBox(id=u"surname")
        age = xul.TextBox(id=u"age")
        
        # a button to submit our form
        submit = xul.Button(label=u"Submit Me")
        
        # a group box to put everything in
        gb = xul.GroupBox(flex=1).append(xul.Caption(
            value=u"A handy-dandy form"))
        
        #lay it all out in a nice grid:
        grid = xul.Grid().append(
            xul.Columns().append(
                xul.Column(flex=4),
                xul.Column(flex=6)
            ),
            xul.Rows().append(
                xul.Row().append(
                    xul.Label(value=u"Firstname"),
                    firstname
                ),
            xul.Row().append(
                    xul.Label(value=u"Surname"),
                    surname
                ),
            xul.Row().append(
                    xul.Label(value=u"Age"),
                    age
                )
            )
        )
        #jam it all together in the window 
        self.window.append(gb.append(grid, submit, self.display))

        #create a FieldAggregate to handle our form
        form = xulform.FieldAggregate()
        form.append(firstname, surname, age)
        form.setSubmitter(submit)
        form.addHandler('oncommand', self.handleSubmit)

    def handleSubmit(self, *args):
        self.display.setAttr(u'value', u"You submitted: %s %s %s" % args)
