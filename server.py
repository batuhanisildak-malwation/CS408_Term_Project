from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLineEdit
from PyQt5.QtCore import pyqtSignal, pyqtSlot
import sys
import socket
import threading
import time

clients = {}
usernames = set()
channels = {"if100": set(), "sps101": set()}

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

class ServerGUI(QWidget):
    update_clients_signal = pyqtSignal()
    update_if100_signal = pyqtSignal()
    update_sps101_signal = pyqtSignal()
    def __init__(self, server):
        super().__init__()
        self.server = server
        self.connected_clients_textbox = QTextEdit()
        self.if100_clients_textbox = QTextEdit()
        self.sps101_clients_textbox = QTextEdit()
        self.initUI()

        self.update_clients_signal.connect(self.update_connected_clients_display)
        self.update_if100_signal.connect(self.update_if100_subscriptions_display)
        self.update_sps101_signal.connect(self.update_sps101_subscriptions_display)

    def initUI(self):
        layout = QVBoxLayout()


        top_layout = QVBoxLayout()

        self.portInput = QLineEdit()
        self.portInput.setPlaceholderText('eg: 6666')
        self.portInput.setStyleSheet(inputStyles)
        top_layout.addWidget(self.portInput)

        self.startButton = QPushButton('Start Server')
        self.startButton.setStyleSheet('background-color: #4BB543; color: white; margin-top: 20px; border-radius: 5px; height: 30px;')
        self.startButton.clicked.connect(self.startServer)
        top_layout.addWidget(self.startButton)

        self.stopButton = QPushButton('Stop Server')
        self.stopButton.setStyleSheet('background-color: #DC3545; color: white; margin-top: 10px; border-radius: 5px; height: 30px;')
        self.stopButton.clicked.connect(self.stopServer)
        top_layout.addWidget(self.stopButton)

        self.logTextBox = QTextEdit()
        self.logTextBox.setReadOnly(True)
        self.logTextBox.setPlaceholderText('Server Logs')
        self.logTextBox.setStyleSheet(message_box_stylesheet)
        top_layout.addWidget(self.logTextBox)

        layout.addLayout(top_layout)

        bottom_layout = QHBoxLayout()
        self.connected_clients_textbox.setReadOnly(True)
        self.connected_clients_textbox.setPlaceholderText('Connected Clients - 0')
        self.connected_clients_textbox.setStyleSheet(message_box_stylesheet)
        bottom_layout.addWidget(self.connected_clients_textbox)

        self.if100_clients_textbox.setReadOnly(True)
        self.if100_clients_textbox.setPlaceholderText('Clients Subscribed to IF100 - 0')
        self.if100_clients_textbox.setStyleSheet(message_box_stylesheet)
        bottom_layout.addWidget(self.if100_clients_textbox)

        self.sps101_clients_textbox.setReadOnly(True)
        self.sps101_clients_textbox.setPlaceholderText('Clients Subscribed to SPS101 - 0')
        self.sps101_clients_textbox.setStyleSheet(message_box_stylesheet)
        bottom_layout.addWidget(self.sps101_clients_textbox)

        layout.addLayout(bottom_layout)

        self.setLayout(layout)
        self.setWindowTitle('DiSUcord Server')
        self.setGeometry(1200, 1200, 1200, 600)

    def startServer(self):
        if self.server.running:
            self.updateLog("Server is already running, invalid operation")
            return
        if self.portInput.text() == '':
            self.updateLog("Please enter a valid port number")
            return
        try:
            port = int(self.portInput.text())
        except:
            self.updateLog("Please enter a valid port number")
            return
        if port < 1024 or port > 65535:
            self.updateLog("These port numbers require root access. Please enter a port number between 1024 and 65535")
            return
        self.server.start(self, port)

    def stopServer(self):
        if not self.server.running:
            self.updateLog("Server is not running, invalid operation")
            return
        self.updateLog("Server is shutting down, please wait...")
        self.server.stop()
        self.close()

    def updateLog(self, message):
        self.logTextBox.append(message)

    @pyqtSlot()
    def update_connected_clients_display(self):
        self.connected_clients_textbox.clear()
        self.connected_clients_textbox.append("\n".join(usernames))

    @pyqtSlot()
    def update_if100_subscriptions_display(self):
        self.if100_clients_textbox.clear()
        for conn in channels["if100"]:
            self.if100_clients_textbox.append(clients[conn])

    @pyqtSlot()
    def update_sps101_subscriptions_display(self):
        self.sps101_clients_textbox.clear()
        for conn in channels["sps101"]:
            self.sps101_clients_textbox.append(clients[conn])

class DiSUcordServer:
    def __init__(self):
        self.HOST = socket.gethostbyname(socket.gethostname()) # this is the IP address of the machine running the server, it makes easy to use docker xd
        self.PORT = 6666 # default port
        self.server_socket = None
        self.running = False
        self.gui = None

    def start(self, gui, port):
        self.PORT = port
        self.gui = gui
        self.running = True
        threading.Thread(target=self.run_server, daemon=True).start()

    def stop(self):
        self.running = False
        self.server_socket.close()

    def run_server(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.HOST, self.PORT))
            self.server_socket.listen()
            self.gui.updateLog(f"Server started. Listening on {self.HOST}:{self.PORT}")

            while self.running:
                try:
                    conn, addr = self.server_socket.accept()
                    threading.Thread(target=self.client_thread, args=(conn, addr)).start()
                except:
                    self.gui.updateLog("Server error")
                    break
        except socket.error as e:
            self.gui.updateLog(f"Socket error: {e}")
    def send_message_to_conn(self, conn, message):
        try:
            conn.send(message.encode('utf-8'))
        except socket.error as e:
            self.gui.updateLog(f"Error sending message: {e}")
            conn.close()
            self.gui.updateLog(f"Client {addr} disconnected")
            for channel in channels.values():
                channel.discard(conn)

    def client_thread(self, conn, addr):
        username = None
        self.gui.updateLog(f"A new client connected - {addr}")
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break

                message = data.decode('utf-8')
                if ":" not in message:
                    self.send_message_to_conn(conn, "Invalid message format. Use command:message")
                    continue

                command, content = message.split(":", 1)
                if command == "username":
                    if content in usernames:
                        self.send_message_to_conn(conn, "Username already in use")
                        self.gui.updateLog(f"{addr} tried to use username {content} which is already in use, aborted")
                    else:
                        usernames.add(content)
                        clients[conn] = content
                        username = content
                        self.send_message_to_conn(conn, "USER_SUCCESS")
                        self.gui.update_clients_signal.emit()
                        self.gui.updateLog(f"Username {content} set for {addr}")

                elif command == "join":
                    # This is a validation for unwanted behaviour, client that I made does not allow this to happen
                    if username is None or username not in usernames or conn not in clients:
                        self.send_message_to_conn(conn, "You must set a username before joining a channel")
                        self.gui.updateLog(f"Client {addr} tried to join channel {content} without setting a username")
                        return;
                    if content in channels:
                        channels[content].add(conn)
                        self.send_message_to_conn(conn, f"CHANNEL_JOIN_SUCCESS_{content}")
                        self.gui.update_if100_signal.emit()
                        self.gui.update_sps101_signal.emit()
                        self.gui.updateLog(f"Client {addr} aKa {'Anonymous User' if username is None else username} joined channel {content}")
                        self.broadcast(f"{content}:Server/{'Anonymous User' if username is None else username} joined the channel", content)
                    else:
                        # This is a validation for unwanted behaviour, client that I made does not allow this to happen
                        self.send_message_to_conn(conn, "Invalid channel")
                        self.gui.updateLog(f"Client {addr} aKa {'Anonymous User' if username is None else username} tried to join invalid channel {content}")
                elif command == "leave":
                    if content in channels and conn in channels[content]:
                        channels[content].discard(conn)
                        self.send_message_to_conn(conn, f"CHANNEL_LEAVE_SUCCESS_{content}")
                        self.gui.update_if100_signal.emit()
                        self.gui.update_sps101_signal.emit()
                        self.gui.updateLog(f"Client {addr} aKa {'Anonymous User' if username is None else username} left channel {content}")
                        self.broadcast(f"{content}:Server/{'Anonymous User' if username is None else username} left the channel", content)
                    else:
                        # This is a validation for unwanted behaviour, client that I made does not allow this to happen
                        self.send_message_to_conn(conn, "Invalid channel")
                        self.gui.updateLog(f"Client {addr} aKa {'Anonymous User' if username is None else username} tried to leave invalid channel {content}")

                elif command == "send":
                    channel, msg = content.split(":", 1)
                    if channel in channels and conn in channels[channel]:
                        self.broadcast(f"{channel}:{username}/{msg}", channel)
                        self.gui.updateLog(f"Client {addr} aKa {'Anonymous User' if username is None else username} sent message to channel {channel}: {msg}")
                    else:
                        self.send_message_to_conn(conn, "SEND_MESSAGE_ERROR_NOT_SUBSCRIBED")
                        self.gui.updateLog(f"Client {addr} aKa {'Anonymous User' if username is None else username} tried to send message to channel {channel} but is not subscribed to it")

                elif command == "list":
                    self.send_message_to_conn(conn, f"Channels: {', '.join(channels.keys())}")
                    self.gui.updateLog(f"Client {addr} aKa {'Anonymous User' if username is None else username} requested channel list")
                elif command == "quit":
                    self.send_message_to_conn(conn, "DISCONNECT")
                    self.gui.update_clients_signal.emit()
                    self.gui.update_if100_signal.emit()
                    self.gui.update_sps101_signal.emit()
                    self.gui.updateLog(f"Client {addr} aKa {'Anonymous User' if username is None else username} disconnected")
                    break
                else:
                    self.gui.update_clients_signal.emit()
                    self.gui.update_if100_signal.emit()
                    self.gui.update_sps101_signal.emit()
                    self.send_message_to_conn(conn, "INVALID_COMMAND")
                    self.gui.updateLog(f"Client {addr} aKa {'Anonymous User' if username is None else username} sent invalid command: {command}")

        except self.server_socket as e:
            self.gui.update_clients_signal.emit()
            self.gui.update_if100_signal.emit()
            self.gui.update_sps101_signal.emit()
            self.gui.updateLog(f"Socket error: {e}")

        finally:
            self.gui.updateLog(f"Client {addr} aKa {'Anonymous User' if username is None else username} disconnected")
            if username:
                usernames.discard(username)
            for channel in channels.values():
                channel.discard(conn)
            conn.close()
            self.gui.update_clients_signal.emit()
            self.gui.update_if100_signal.emit()
            self.gui.update_sps101_signal.emit()

    def broadcast(self, message, channel):
        for client in channels[channel]:
            try:
                client.send(message.encode('utf-8'))
            except socket.error as e:
                self.gui.updateLog(f"Error sending message: {e}")
                client.close()
                channels[channel].discard(client)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    server = DiSUcordServer()
    ex = ServerGUI(server)
    ex.show()
    sys.exit(app.exec_())
