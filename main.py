import sys
import re
from PyQt6.QtWidgets import QApplication, QWidget, QTextEdit, QLineEdit, QPushButton, QGridLayout
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from threading import *
from time import sleep

from connection import *
from htmlManager import *
from encryption import *

isRunning = True

connect()

def send_message():
    msg = entry_field.text()
    if msg != "":
        htmlManager.addMessageBubble("You", msg, left=False)
        entry_field.setText("")
        if msg.startswith("/server "):
            send(msg.removeprefix("/server "), b"ISCs")
        elif msg.startswith(("/shift ", "/vigenere ", "/RSA ", "/hash")):
            encode_srv_message(msg)
        else:
            send(msg, b"ISCt")

def encode_srv_message(msg):
    codemsg_pattern = r'^/(shift|vigenere|RSA|hash) "([^"]+)"(?: "([^"]+)")?$'
    regMatch = re.match(codemsg_pattern, msg)
    if regMatch:
        encodedMsg = ""
        match msg.split()[0]:
            case "/shift": encodedMsg = f"shift: {encrypt_shift(regMatch.group(2), regMatch.group(3))}"
            case "/vigenere": encodedMsg = f"vigenere: {encrypt_vigenere(regMatch.group(2), regMatch.group(3))}"
            case "/RSA": encodedMsg = "RSA: -"
            case "/hash": encodedMsg = f"hash: {hash(regMatch.group(2))}"
        htmlManager.addMessageBubble("ISC Chat", f"Message encoded with {encodedMsg}")
    else:
        htmlManager.addMessageBubble("ISC Chat", "Wrong command syntax")

def receive_message():
    while isRunning:
        result = listen()
        if result:
            type, msg = result
            if msg is not None and msg != "":
                if type=='t':
                    htmlManager.addMessageBubble("User", msg)
                elif type=='s':
                    htmlManager.addMessageBubble("Server", msg)
        sleep(0.1)

def key_handler(event):
    if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
        send_message()
    else:
        QLineEdit.keyPressEvent(entry_field, event)

def stop_listening():
    global isRunning
    isRunning = False
    sleep(1)

def close_event(event):
    event.accept()
    stop_listening()

    send("", b"ISCt")
    listening.join()

try:
    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("ISC Secured Chat")
    window.setGeometry(100, 100, 600, 800)
    window.setWindowIcon(QIcon("img/isc-logo.png"))

    htmlManager = HtmlManager(window)

    entry_field = QLineEdit(window)
    entry_field.setPlaceholderText("Type your message here...")

    send_button = QPushButton(">", window)
    send_button.clicked.connect(send_message)

    # Add key listener to entry_field
    entry_field.keyPressEvent = key_handler

    # Grid management
    gLayout = QGridLayout(window)
    gLayout.addWidget(htmlManager.chat_area, 0, 0, 1, 2)
    gLayout.addWidget(entry_field, 1, 0)
    gLayout.addWidget(send_button, 1, 1)
    gLayout.setRowStretch(0, 1)
    gLayout.setRowStretch(1, 0)

    # Listen to messages
    listening = Thread(target=receive_message)
    listening.daemon = True
    listening.start()

    window.setLayout(gLayout)

    window.closeEvent = close_event

    window.show()

    sys.exit(app.exec())

except Exception as e:
    print(f"An error occurred: {e}")