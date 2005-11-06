"""Support for traditional 'forms' in XUL."""


class FieldAggregate(object):
    """I hold a list of fields and have a submitter widget (usually a
    button) On submit I call the handler passing it the value of each
    field.
    
    firstname = xul.TextBox(id='firstname')
    lastname = xul.TextBox(id='lastname')
    submit = xul.Button(label='Submit')
    
    form = FieldAggregate()
    form.append(firstname, lastname)
    form.setSubmitter(submit)
    form.addHandler('oncommand', myFunc)

    myFunc will be called with the field  values, it is up to you
    to ensure all fields are live at the time the event is fired.
    """

    def __init__(self):
        self.fields = []
        self.submitter = None
        
    def append(self, *kwargs):
        if self.submitter and len(self.submitter.handlers.keys()) != 0:
            raise RuntimeError, "Cannot append fields after calling addHandler"
        self.fields += kwargs
    
    def setSubmitter(self, widget):
        self.submitter = widget
        
    def addHandler(self, event, func):
        if not self.submitter:
            raise RuntimeError, "Cannot call addHandler before setSubmitter"
        else:
            fields = [f.requestAttr('value') for f in self.fields]
            self.submitter.addHandler(event, func, *fields)
