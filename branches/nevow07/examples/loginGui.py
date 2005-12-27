from nufox import xul
from nufox import xulform


class LoginGUI(xul.XULPage):

    def setup(self):
        self.window = xul.Window(
            title=u"Login",
            width=400,height=400,
            style=u"background-color:#D7DBD6;",
            )
        self.lblProductTitle = xul.Label(
            value=u"Stock Management System",
            style=(u'text-align: center;'
                   u'color: #464844;'
                   u'font-size: 1.5em;'
                   u'font-weight: bold;'
                   ),
            )
        self.lblLic = xul.Label(
            value=u"Abaker Printing Co.",
            style=(u'text-align: center;'
                   u'color: #5B6560;'
                   u'font-size: 1em;'
                   u'font-weight: bold;'
                   ),
            )
        self.lblUserName = xul.Label(
            value=u"Username:",
            style=(u'text-align: right;'
                   u'color: #464844;'
                   u'font-size: 1.3em;'
                   ),
            )
        self.txtUserName = xul.TextBox(size="30")
        self.lblPassword = xul.Label(
            value=u"Password:",
            style=(u'text-align: right;'
                   u'color: #464844;'
                   u'font-size:1.3em;',
                   ),
            )
        self.txtPassword = xul.TextBox(size=u"30",type=u"password")
        self.btnLogin = xul.Button(label=u"Login",accesskey=u"L")
        self.btnCancel = xul.Button(label=u"Cancel",accesskey=u"C")
        self.__do_layout()

    def __do_layout(self):
        self.loginGroupBox = xul.VBox(flex=1)
        self.mainLayout = xul.VBox()
        self.entryGrid = xul.Grid()
        self.entryColumns = xul.Columns()
        self.entryRows = xul.Rows()
        self.entryColumns.append(xul.Column(flex=4))
        self.entryColumns.append(xul.Column(flex=1))
        self.entryColumns.append(xul.Column(flex=1))
        self.entryColumns.append(xul.Column(flex=4))
        self.entryRows.append(
            xul.Row().append(xul.Spacer(),self.lblUserName,self.txtUserName,
                             xul.Spacer()))
        self.entryRows.append(
            xul.Row().append(xul.Spacer(),self.lblPassword,self.txtPassword,
                             xul.Spacer()))
        self.entryGrid.append(self.entryColumns,self.entryRows)
        self.buttonLayout = xul.HBox()
        self.buttonLayout.append(xul.Spacer(flex=4))
        self.buttonLayout.append(self.btnLogin)
        self.buttonLayout.append(self.btnCancel)
        self.buttonLayout.append(xul.Spacer(flex=4))
        self.mainLayout.append(xul.Spacer(height=25))
        self.mainLayout.append(self.lblProductTitle)
        self.mainLayout.append(self.lblLic)
        self.mainLayout.append(xul.Spacer(height=25))
        self.mainLayout.append(self.entryGrid)
        self.mainLayout.append(xul.Spacer(height=25))
        self.mainLayout.append(self.buttonLayout)
        self.loginGroupBox.append(self.mainLayout)
        self.window.append(self.loginGroupBox)


class Example(LoginGUI):
    """Login GUI (debug me)"""

    discussion = """
    Contributed by Alagu Madhu.
    """

    def setup(self):
        LoginGUI.setup(self)
        form = xulform.FieldAggregate()
        form.append(self.txtUserName, self.txtPassword)
        form.setSubmitter(self.btnLogin)
        form.addHandler('oncommand', self.onLogin)

    def onLogin(self, *args):
        print u"Got username: %r, password: %r" % args


