from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QTextEdit, QHBoxLayout, QFrame
from PyQt5.QtCore import pyqtSignal, pyqtSlot
import socket
import sys
import threading

inputStyles = """
QLineEdit {
    border: 1px solid #343a40;
    border-radius: 4px;
    padding: 6px 12px;
    background-color: #2C2C2E;
    color: #ffffff;
    font-size: 18px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}
"""

# I am not a good designer but, better than the default one, I guess :P
message_box_stylesheet = """
QTextEdit {
    background-color: #2C2C2E;
    color: #FFFFFF;
    border: 1px solid #3A3A3C;
    border-radius: 10px;
    padding: 10px;
    font-size: 15px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}
"""

class ClientGUI(QWidget):

    message_received = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.socket = None
        self.connected = False
        self.initUI()
        self.message_received.connect(self.displayMessage)

    def initUI(self):
        self.layout = QVBoxLayout(self)


        self.connectionFrame = QFrame(self)
        self.connectionLayout = QVBoxLayout()

        self.hostInput = QLineEdit(self)
        self.hostInput.setPlaceholderText('Enter Host')
        self.hostInput.setStyleSheet(inputStyles)
        self.connectionLayout.addWidget(self.hostInput)

        self.portInput = QLineEdit(self)
        self.portInput.setPlaceholderText('Enter Port')
        self.portInput.setStyleSheet(inputStyles)
        self.connectionLayout.addWidget(self.portInput)

        self.usernameInput = QLineEdit(self)
        self.usernameInput.setPlaceholderText('Enter Username')
        self.usernameInput.setStyleSheet(inputStyles)
        self.connectionLayout.addWidget(self.usernameInput)

        self.connectButton = QPushButton('Connect to Server', self)
        self.connectButton.clicked.connect(self.connectToServer)
        self.connectButton.setStyleSheet('background-color: #4BB543; font-size: 18px; color: white; margin-top: 20px; border-radius: 5px; height: 30px;')
        self.connectionLayout.addWidget(self.connectButton)

        self.statusLabel = QLabel(self)
        self.connectionLayout.addWidget(self.statusLabel)

        self.connectionFrame.setLayout(self.connectionLayout)
        self.layout.addWidget(self.connectionFrame)
        self.connectionFrame.show()

        self.chatFrame = QFrame(self)
        self.chatLayout = QVBoxLayout()
        self.createChannelUI('if100')
        self.createChannelUI('sps101')

        self.disconnectButton = QPushButton('Disconnect from Server', self)
        self.disconnectButton.clicked.connect(self.disconnectFromServer)
        self.disconnectButton.setStyleSheet('background-color: #DC3545; font-size: 18px; color: white; margin-top: 10px; border-radius: 5px; height: 30px;')
        self.chatLayout.addWidget(self.disconnectButton)

        self.chatFrame.setLayout(self.chatLayout)
        self.layout.addWidget(self.chatFrame)
        self.chatFrame.hide()

        self.setWindowTitle('DiSUcord Server')
        self.setGeometry(1200, 1200, 1200, 600)
        self.setLayout(self.layout)

    def createChannelUI(self, channelName):
        channelLabel = QLabel(f"{channelName.upper()} Channel", self)
        self.chatLayout.addWidget(channelLabel)

        if channelName == 'if100':
            self.if100Text = QTextEdit(self)
            self.if100Text.setReadOnly(True)
            self.if100Text.setStyleSheet(message_box_stylesheet)
            self.chatLayout.addWidget(self.if100Text)

            self.if100MessageInput = QLineEdit(self)
            self.if100MessageInput.setPlaceholderText('Enter Message')
            self.if100MessageInput.setStyleSheet(inputStyles)
            self.chatLayout.addWidget(self.if100MessageInput)

            self.sendToIf100Button = QPushButton('Send Message', self)
            self.sendToIf100Button.clicked.connect(lambda: self.sendMessage('if100', self.if100MessageInput.text(), self.if100MessageInput))
            self.sendToIf100Button.setVisible(False)
            self.chatLayout.addWidget(self.sendToIf100Button)

            self.connectToIf100Button = QPushButton('Connect to IF100 Channel', self)
            self.connectToIf100Button.clicked.connect(lambda: self.connectToChannel('if100', self.sendToIf100Button, self.connectToIf100Button, self.disconnectFromIf100Button))
            self.connectToIf100Button.setVisible(True)
            self.connectToIf100Button.setStyleSheet('background-color: #4BB543; font-size: 18px; color: white; margin-top: 10px; border-radius: 5px; height: 30px;')
            self.chatLayout.addWidget(self.connectToIf100Button)

            self.disconnectFromIf100Button = QPushButton('Disconnect from IF100 Channel', self)
            self.disconnectFromIf100Button.clicked.connect(lambda: self.disconnectFromChannel('if100', self.sendToIf100Button, self.connectToIf100Button, self.disconnectFromIf100Button, self.if100Text))
            self.disconnectFromIf100Button.setVisible(False)
            self.disconnectFromIf100Button.setStyleSheet('background-color: #FF5F15; font-size: 18px; color: white; margin-top: 10px; border-radius: 5px; height: 30px;')
            self.chatLayout.addWidget(self.disconnectFromIf100Button)
        elif channelName == 'sps101':
            self.sps101Text = QTextEdit(self)
            self.sps101Text.setReadOnly(True)
            self.sps101Text.setStyleSheet(message_box_stylesheet)
            self.chatLayout.addWidget(self.sps101Text)

            self.sps101MessageInput = QLineEdit(self)
            self.sps101MessageInput.setPlaceholderText('Enter Message')
            self.sps101MessageInput.setStyleSheet(inputStyles)
            self.chatLayout.addWidget(self.sps101MessageInput)

            self.sendToSps101Button = QPushButton('Send Message', self)
            self.sendToSps101Button.clicked.connect(lambda: self.sendMessage('sps101', self.sps101MessageInput.text(), self.sps101MessageInput))
            self.sendToSps101Button.setVisible(False)
            self.chatLayout.addWidget(self.sendToSps101Button)

            self.connectToSps101Button = QPushButton('Connect to SPS101 Channel', self)
            self.connectToSps101Button.clicked.connect(lambda: self.connectToChannel('sps101', self.sendToSps101Button, self.connectToSps101Button, self.disconnectFromSps101Button))
            self.connectToSps101Button.setVisible(True)
            self.connectToSps101Button.setStyleSheet('background-color: #4BB543; font-size: 18px; color: white; margin-top: 10px; border-radius: 5px; height: 30px;')
            self.chatLayout.addWidget(self.connectToSps101Button)

            self.disconnectFromSps101Button = QPushButton('Disconnect from SPS101 Channel', self)
            self.disconnectFromSps101Button.clicked.connect(lambda: self.disconnectFromChannel('sps101', self.sendToSps101Button, self.connectToSps101Button, self.disconnectFromSps101Button, self.sps101Text))
            self.disconnectFromSps101Button.setVisible(False)
            self.disconnectFromSps101Button.setStyleSheet('background-color: #FF5F15; font-size: 18px; color: white; margin-top: 10px; border-radius: 5px; height: 30px;')
            self.chatLayout.addWidget(self.disconnectFromSps101Button)

    def connectToServer(self):
        host = self.hostInput.text()
        port = int(self.portInput.text())
        username = self.usernameInput.text()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((host, port))
            # format: username:{username}
            self.socket.send(f"username:{username}".encode('utf-8'))
            response = self.socket.recv(1024).decode('utf-8')
            print(response)
            if response == "USER_SUCCESS":
                self.connected = True
                self.connectionFrame.hide()
                self.chatFrame.show()
                threading.Thread(target=self.receiveMessages, daemon=True).start()
            else:
                self.statusLabel.setText(response)
        except Exception as e:
            self.statusLabel.setText('Connection failed, please make sure that the host and port are correct.')

    def disconnectFromServer(self):
        if self.socket:
            self.socket.send('command:quit'.encode('utf-8'))
            self.connected = False
            self.socket.close()
        self.close()

    @pyqtSlot(str, str)
    def displayMessage(self, channel, message):
        # Logic to display the message in the correct channel's message box
        parsedMessage = message.replace('/', ': ') # Replace the / with : to make it look nicer, just a little parsing
        if channel == 'if100':
            self.if100Text.append(parsedMessage)
        elif channel == 'sps101':
            self.sps101Text.append(parsedMessage)
    def receiveMessages(self):
        while self.connected:
            try:
                message = self.socket.recv(1024).decode('utf-8')
                if message:
                    if ":" not in message:
                        if "SUCCESS" in message:
                            print(message)
                        continue
                    else:
                        channel, msg = message.split(':')
                        print(f"Received message: {msg} from channel {channel}")
                        self.message_received.emit(channel, msg)  # Emit the signal
            except Exception as e:
                print(f"An error occurred: {e}")
                self.socket.close()
                break

    def connectToChannel(self, channelName, sendButton, connectButton, disconnectButton):
        if self.socket and self.connected:
            join_message = f"join:{channelName}"
            print(join_message)
            self.socket.send(join_message.encode('utf-8'))
            sendButton.setVisible(True)
            connectButton.setVisible(False)
            disconnectButton.setVisible(True)

    def disconnectFromChannel(self, channelName, sendButton, connectButton, disconnectButton, textBox):
        if self.socket and self.connected:
            leave_message = f"leave:{channelName}"
            print(leave_message)
            self.socket.send(leave_message.encode('utf-8'))
            sendButton.setVisible(False)
            connectButton.setVisible(True)
            disconnectButton.setVisible(False)
            textBox.setText('')

    def sendMessage(self, channelName, message, messageInput):
        if self.socket and self.connected:
            send_message = f"send:{channelName}:{message}"
            self.socket.send(send_message.encode('utf-8'))
            messageInput.setText('')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ClientGUI()
    ex.show()
    sys.exit(app.exec_())
