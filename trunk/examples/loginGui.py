"""Contributed by Alagu Madhu"""

from nufox import xul
from nufox import xulform


class LoginGUI(xul.XULPage):

    def setup(self):
        self.window = xul.Window(
            title="Login",
            width=400,height=400,
            style="background-color:#D7DBD6;",
            )
        self.lblProductTitle = xul.Label(
            value="Stock Management System",
            style=('text-align: center;'
                   'color: #464844;'
                   'font-size: 1.5em;'
                   'font-weight: bold;'
                   ),
            )
        self.lblLic = xul.Label(
            value="Abaker Printing Co.",
            style=('text-align: center;'
                   'color: #5B6560;'
                   'font-size: 1em;'
                   'font-weight: bold;'
                   ),
            )
        self.lblUserName = xul.Label(
            value="Username:",
            style=('text-align: right;'
                   'color: #464844;'
                   'font-size: 1.3em;'
                   ),
            )
        self.txtUserName = xul.TextBox(size="30")
        self.lblPassword = xul.Label(
            value="Password:",
            style=('text-align: right;'
                   'color: #464844;'
                   'font-size:1.3em;',
                   ),
            )
        self.txtPassword = xul.TextBox(size="30",type="password")
        self.btnLogin = xul.Button(label="Login",accesskey="L")
        self.btnCancel = xul.Button(label="Cancel",accesskey="C")
        self.__do_layout()

    def __do_layout(self):
        self.loginGroupBox = xul.VBox(flex="1")
        self.mainLayout = xul.VBox()
        self.entryGrid = xul.Grid()
        self.entryColumns = xul.Columns()
        self.entryRows = xul.Rows()
        self.entryColumns.append(xul.Column(flex="4"))
        self.entryColumns.append(xul.Column(flex="1"))
        self.entryColumns.append(xul.Column(flex="1"))
        self.entryColumns.append(xul.Column(flex="4"))
        self.entryRows.append(
            xul.Row().append(xul.Spacer(),self.lblUserName,self.txtUserName,
                             xul.Spacer()))
        self.entryRows.append(
            xul.Row().append(xul.Spacer(),self.lblPassword,self.txtPassword,
                             xul.Spacer()))
        self.entryGrid.append(self.entryColumns,self.entryRows)
        self.buttonLayout = xul.HBox()
        self.buttonLayout.append(xul.Spacer(flex="4"))
        self.buttonLayout.append(self.btnLogin)
        self.buttonLayout.append(self.btnCancel)
        self.buttonLayout.append(xul.Spacer(flex="4"))
        self.mainLayout.append(xul.Spacer(height="25"))
        self.mainLayout.append(self.lblProductTitle)
        self.mainLayout.append(self.lblLic)
        self.mainLayout.append(xul.Spacer(height="25"))
        self.mainLayout.append(self.entryGrid)
        self.mainLayout.append(xul.Spacer(height="25"))
        self.mainLayout.append(self.buttonLayout)
        self.loginGroupBox.append(self.mainLayout)
        self.window.append(self.loginGroupBox)


class Example(LoginGUI):

    def setup(self):
        LoginGUI.setup(self)
        form = xulform.FieldAggregate()
        form.append(self.txtUserName, self.txtPassword)
        form.setSubmitter(self.btnLogin)
        form.addHandler('oncommand', self.onLogin)

    def onLogin(self, *args):
        print u"Got username: %r, password: %r" % args

