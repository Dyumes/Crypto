import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPlainTextEdit, QLineEdit, QPushButton, QGridLayout
from PyQt6.QtCore import Qt
from connection import *
from threading import *

connect()

def send_message():
    msg = entry_field.text()
    if msg != '':
        chat_area.insertPlainText(f"\n<You> {msg}")
        chat_area.update()
        entry_field.setText("")
        send(msg)

def receive_message():
    while True:
        (type, msg) = listen()
        if msg!=None and msg != '':
            if type=='t':
                chat_area.insertPlainText(f"\n<User> {msg}")
            elif type=='s':
                chat_area.insertPlainText(f"\n<Server> {msg}")
            chat_area.update()

def key_handler(event):
    if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
        send_message()
    else:
        QLineEdit.keyPressEvent(entry_field, event)

try:
    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("ChatApp")
    window.setGeometry(100, 100, 600, 800)

    chat_area = QPlainTextEdit(window)
    chat_area.setReadOnly(True)

    entry_field = QLineEdit(window)
    entry_field.setPlaceholderText("Type your message here...")

    send_button = QPushButton(">", window)
    send_button.clicked.connect(send_message)

    # Add key listener to entry_field
    entry_field.keyPressEvent = key_handler

    # Grid management
    gLayout = QGridLayout(window)
    gLayout.addWidget(chat_area, 0, 0, 1, 2)
    gLayout.addWidget(entry_field, 1, 0)
    gLayout.addWidget(send_button, 1, 1)
    gLayout.setRowStretch(0, 1)
    gLayout.setRowStretch(1, 0)

    # Listen to messages
    listening = Thread(target=receive_message)
    listening.start()

    window.setLayout(gLayout)

    window.show()

    app.exec()

except Exception as e:
    print(f"An error occurred: {e}")