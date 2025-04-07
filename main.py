import sys
import re
from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QGridLayout
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
        elif msg.startswith(("/shift ", "/vigenere ", "/rsa ", "/hash", "/difhel")):
            encode_srv_message(msg)
        else:
            send(msg, b"ISCt")

def encode_srv_message(msg):
    # Define the command patterns
    codemsg_patterns = {
        'shift': r'^/shift\s+"([^"]+)"\s+"([^"]+)"$',                           # /shift "something" "something"
        'vigenere': r'^/vigenere\s+"([^"]+)"\s+"([^"]+)"$',                     # /vigenere "something" "something"
        'rsa': r'^/rsa\s+"([^"]+)"\s+"([^"]+)"\s+"([^"]+)"$',                   # /RSA "something" "something" "something"
        'hash': r'^/hash\s+"([^"]+)"$',                                         # /hash "something"
        'difhel': r'^/difhel\s*$',                                              # /difhel (no parameters)
        'difhel_with_params': r'^/difhel\s+"([^"]+)"\s+"([^"]+)"\s+"([^"]+)"$', # /difhel "something" "something" "something"
    }
    # Check for each command type
    found_syntax = False
    for cmd, pattern in codemsg_patterns.items():
        # codemsg_pattern = r'^/(shift|vigenere|RSA|hash) "([^"]+)"(?: "([^"]+)")?(?: "([^"]+)")?$'
        regMatch = re.match(pattern, msg)
        if regMatch:
            found_syntax = True
            encodedMsg = ""
            server_message = ""
            #match msg.split()[0]:
            #    case "/shift": 
            #        server_message = encrypt_shift(regMatch.group(2), regMatch.group(3))
            #        encodedMsg = f"shift: {server_message}"
            #    case "/vigenere": 
            #        server_message =  encrypt_vigenere(regMatch.group(2), regMatch.group(3))
            #        encodedMsg = f"vigenere: {server_message}"
            #    case "/RSA": 
            #        server_message = encrypt_rsa(regMatch.group(2), regMatch.group(3), regMatch.group(4))
            #        text_to_add = ""
            #        text_to_add += bytes(b for b in server_message if b != 0).decode('utf-8', 'replace')
            #        encodedMsg = f"RSA: {text_to_add}"
            #    case "/hash": 
            #        server_message = hash(regMatch.group(2)) 
            #        encodedMsg = f"Hash encode: {server_message}"
            # Command matched, handle accordingly
            if cmd == 'shift':
                shiftmsg, shiftkey = regMatch.groups()
                server_message = encrypt_shift(shiftmsg, shiftkey)
                encodedMsg = f"Message encoded with shift: {server_message}"
            elif cmd == 'vigenere':
                vigmsg, vigkey = regMatch.groups()
                server_message =  encrypt_vigenere(vigmsg, vigkey)
                encodedMsg = f"Message encoded with vigenere: {server_message}"
            elif cmd == 'rsa':
                rsamsg, rsan, rsae = regMatch.groups()
                server_message = encrypt_rsa(rsamsg, rsan, rsae)
                text_to_add = ""
                text_to_add += bytes(b for b in server_message if b != 0).decode('utf-8', 'replace')
                encodedMsg = f"Message encoded with RSA: {text_to_add}"
            elif cmd == 'hash':
                hashmsg = regMatch.groups()[0]
                server_message = hash(hashmsg)
                encodedMsg = f"Message encoded with Hash: {server_message}"
            elif cmd == 'difhel':
                p, g = generate_difhel()
                server_message = f"{p},{g}"
                encodedMsg = f"Diffie-Hellman generated modular: {p} and generator: {g}"
            elif cmd == 'difhel_with_params':
                difhelP, difhelG, gB = regMatch.groups()
                gA, secretDH = secret_difhel(difhelP, difhelG, gB)
                encodedMsg = f"Diffie-Hellman generated half-key: {gA}"
                htmlManager.addMessageBubble("ISC Chat", encodedMsg)
                send(str(gA), b"ISCs")
                server_message = str(secretDH)
                encodedMsg = f"Diffie-Hellman founded secret: {secretDH}"

            htmlManager.addMessageBubble("ISC Chat", encodedMsg)
            send(server_message, b"ISCs")

    if found_syntax == False:
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