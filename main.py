import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLabel, QTextEdit, QLineEdit
from ldap3 import Server, Connection, ALL

class FileDiffApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        mainLayout = QVBoxLayout()

        buttonLayout = QHBoxLayout()

        # Master Hosts button, AD input, button and text box
        self.masterLayout = QVBoxLayout()

        self.browseButton1 = QPushButton("Master Hosts", self)
        self.browseButton1.clicked.connect(lambda: self.loadFile(1))
        self.masterLayout.addWidget(self.browseButton1)

        self.adInput = QLineEdit(self)  # Line edit for OU DN
        self.adInput.setPlaceholderText("Enter OU DN (e.g., OU=Your_OU,DC=Your_Domain,DC=com)")
        self.masterLayout.addWidget(self.adInput)

        self.adButton = QPushButton("Fetch from AD", self)
        self.adButton.clicked.connect(self.fetchFromAD)
        self.masterLayout.addWidget(self.adButton)

        self.masterTextBox = QTextEdit(self)
        self.masterTextBox.setReadOnly(True)
        self.masterLayout.addWidget(self.masterTextBox)
        buttonLayout.addLayout(self.masterLayout)

        # Hosts to Check button and text box
        self.checkLayout = QVBoxLayout()
        self.browseButton2 = QPushButton("Hosts to Check", self)
        self.browseButton2.clicked.connect(lambda: self.loadFile(2))
        self.checkLayout.addWidget(self.browseButton2)
        self.checkTextBox = QTextEdit(self)
        self.checkTextBox.setReadOnly(True)
        self.checkLayout.addWidget(self.checkTextBox)
        buttonLayout.addLayout(self.checkLayout)

        mainLayout.addLayout(buttonLayout)

        # Difference button, difference text box, and status label
        self.diffButton = QPushButton("Difference", self)
        self.diffButton.clicked.connect(self.findDifference)
        mainLayout.addWidget(self.diffButton)

        self.diffTextBox = QTextEdit(self)
        self.diffTextBox.setReadOnly(True)
        mainLayout.addWidget(self.diffTextBox)

        self.statusLabel = QLabel("", self)
        mainLayout.addWidget(self.statusLabel)

        self.setLayout(mainLayout)
        self.setWindowTitle('Find Difference Between Files')
        self.setGeometry(300, 300, 600, 600)

    def loadFile(self, file_number):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(self, "Open Text File", "", "Text Files (*.txt);;All Files (*)", options=options)
        if filePath:
            with open(filePath, 'r') as file:
                content = file.read()

            if file_number == 1:
                self.masterTextBox.setText(content)
                self.statusLabel.setText(f"Master Hosts loaded from: {filePath}")
            elif file_number == 2:
                self.checkTextBox.setText(content)
                self.statusLabel.setText(f"Hosts to Check loaded from: {filePath}")

    def findDifference(self):
        master_hostnames = set(self.masterTextBox.toPlainText().splitlines())
        check_hostnames = set(self.checkTextBox.toPlainText().splitlines())
        diff = master_hostnames - check_hostnames

        diff_str = '\n'.join(diff)
        self.diffTextBox.setText(diff_str)

        self.statusLabel.setText('Differences displayed below.')

    def fetchFromAD(self):
        ou = self.adInput.text()
        if ou:
            ad_server = "your_ad_server.domain.com"  # Adjust as needed
            ad_user = "CN=your_username,OU=Users,DC=Your_Domain,DC=com"  # Adjust as needed
            ad_pass = "your_password"  # Adjust and consider a more secure method
            hostnames = self.fetch_hostnames_from_ad(ou, ad_server, ad_user, ad_pass)
            self.masterTextBox.setText('\n'.join(hostnames))
        else:
            self.statusLabel.setText('Please enter an OU DN.')

    def fetch_hostnames_from_ad(self, ou, ad_server, ad_user, ad_pass, protocol='ldaps'):
        server = Server(f'{protocol}://{ad_server}', use_ssl=(protocol == 'ldaps'), get_info=ALL)
        conn = Connection(server, user=ad_user, password=ad_pass, auto_bind=True)

        search_filter = '(objectClass=computer)'
        attributes = ['name']

        conn.search(search_base=ou, search_filter=search_filter, attributes=attributes)
        hostnames = [entry['attributes']['name'] for entry in conn.entries]
        return hostnames

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FileDiffApp()
    ex.show()
    sys.exit(app.exec_())
