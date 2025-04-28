import sys
import re
from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QGridLayout, QHBoxLayout, QLabel, QVBoxLayout
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt
from threading import *
from time import sleep

from connection import *
from htmlManager import *
from encryption import *

# =============================================
# Global Variables
# =============================================
encryption_type = None  # Tracks current encryption method (shift/vigenere/RSA/hash/difhel)
isRunning = True       # Controls the receive_message thread loop

# =============================================
# Network Initialization
# =============================================
connect()  # Establish socket connection (defined in connection.py)

# =============================================
# Message Sending Logic
# =============================================
def send_message():
    global encryption_type
    msg = entry_field.text()
    if msg != "":
        # Display user's message in chat
        htmlManager.addMessageBubble("You", msg, left=False)
        entry_field.setText("")
        
        # Handle server commands (encryption type selection)
        if msg.startswith("/server "):
            if "shift" in msg:
                encryption_type = "shift"
            elif "vigenere" in msg:
                encryption_type = "vigenere"
            elif "RSA" in msg:
                encryption_type = "RSA"
            elif "hash" in msg:
                encryption_type = "hash"
            elif "difhel" in msg:
                encryption_type = "difhel"
            print(f"Encryption type required : {encryption_type}")
            send(msg.removeprefix("/server "), b"ISCs")  # Send to server channel
            
        # Handle encryption commands
        elif msg.startswith(("/shift ", "/vigenere ", "/rsa ", "/hash", "/difhel")):
            encode_srv_message(msg)
            
        # Default message sending
        else:
            send(msg, b"ISCt")  # Send to text channel

# =============================================
# Server Command Processing
# =============================================
def encode_srv_message(msg):
    # Command patterns with regex
    codemsg_patterns = {
        'shift': r'^/shift\s+"([^"]+)"\s+"([^"]+)"$',                           #/shift "message" "key"
        'vigenere': r'^/vigenere\s+"([^"]+)"\s+"([^"]+)"$',                     #/vigenere "message" "key"
        'rsa': r'^/rsa\s+"([^"]+)"\s+"([^"]+)"\s+"([^"]+)"$',                   #/rsa "message" "n" "e"
        'hash': r'^/hash\s+"([^"]+)"$',                                         #/hash "message"    
        'hash verify': r'^/hash verify\s+"([^"]+)"\s+"([^"]+)"$',               #/hash verify "message" "hash"
        'difhel': r'^/difhel\s*$',                                              #/difhel         
        'difhel_with_params': r'^/difhel\s+"([^"]+)"\s+"([^"]+)"\s+"([^"]+)"$', #/sifhel "p" "g" "gB"
    }
    
    found_syntax = False
    for cmd, pattern in codemsg_patterns.items():
        regMatch = re.match(pattern, msg)
        if regMatch:
            found_syntax = True
            encodedMsg = ""
            server_message = ""
            
            # Shift encryption
            if cmd == 'shift':
                shiftmsg, shiftkey = regMatch.groups()
                shiftkey = int(shiftkey)
                server_message = encrypt_shift(shiftmsg, shiftkey)
                encodedMsg = f"Message encoded with shift: {server_message}"
                htmlManager.addMessageBubble("ISC Chat", server_message.decode('utf-8', 'replace'))
                break
                
            # Vigenère encryption
            elif cmd == 'vigenere':
                vigmsg, vigkey = regMatch.groups()
                server_message = encrypt_vigenere(vigmsg, vigkey)
                encodedMsg = f"Message encoded with vigenere: {server_message}"
                htmlManager.addMessageBubble("ISC Chat", server_message.decode('utf-8', 'replace'))
                break
                
            # RSA encryption
            elif cmd == 'rsa':
                rsamsg, rsan, rsae = regMatch.groups()
                server_message = encrypt_rsa(rsamsg, rsan, rsae)
                text_to_add = bytes(b for b in server_message if b != 0).decode('utf-8', 'replace')
                encodedMsg = f"Message encoded with RSA: {text_to_add}"
                htmlManager.addMessageBubble("ISC Chat", server_message.decode('utf-8', 'replace'))
                break
                
            # Hashing
            elif cmd == 'hash':
                hashmsg = regMatch.groups()[0]
                server_message = hash(hashmsg)
                encodedMsg = f"Message encoded with Hash: {server_message}"
                htmlManager.addMessageBubble("ISC Chat", server_message.decode('utf-8', 'replace'))
                break
                
            # Hash verification
            elif cmd == 'hash verify':
                msg_to_hash = regMatch.groups()[0]
                hashmsg = regMatch.groups()[1]
                server_message = hashVerify(msg_to_hash, hashmsg)
                encodedMsg = f"Is the hash corresponding: {server_message}"
                send(server_message, b"ISCs")
                break
                
            # Diffie-Hellman key exchange
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

            # Display and send results
            htmlManager.addMessageBubble("ISC Chat", encodedMsg)
            send(server_message, b"ISCs")

    if not found_syntax:
        htmlManager.addMessageBubble("ISC Chat", "Wrong command syntax")

# =============================================
# Message Receiving Logic
# =============================================
key_found = False
encryption_key = None
msg_to_encrypt = ""
next_server_msg = False

def extract_encryption_keys(msg):
    global encryption_type
    """Extracts encryption parameters from server messages"""
    # Shift key extraction
    match = re.search(r"You are asked to encode the text in the following message with the shift-key ([^\n]+)", msg)
    print(encryption_type)
    if match and encryption_type == "shift":
        shift_key = int(match.group(1))
        print(f"Extracted shift key for shift: {shift_key}")
        return shift_key
    
    # Vigenère key extraction
    if match and encryption_type == "vigenere":
        shift_key = match.group(1)
        print(f"Extracted shift key for vigenere: {shift_key}")
        return shift_key
    
    # RSA keys extraction
    rsa_match = re.search(r"You are asked to encode the text in the following message with the key n=(\d+), e=(\d+)", msg)
    if rsa_match and encryption_type == "RSA":
        rsa_n = int(rsa_match.group(1))
        rsa_e = int(rsa_match.group(2))
        print(f"Extracted RSA keys: n={rsa_n}, e={rsa_e}")
        return rsa_n, rsa_e
    
    return None

def receive_message():
    global key_found, msg_found, shift_key, msg_to_encrypt, next_server_msg
    
    while isRunning:
        try:
            # 1. Receive header (4 bytes)
            header = sock.recv(4)
            if len(header) != 4:
                continue
                
            # Verify protocol header
            if header[:3] != b'ISC':
                print("Invalid protocol header")
                continue
                
            # Message type (t=text, s=server, i=info)
            msg_type = header[3:4].decode('ascii')
            
            # 2. Receive message length (2 bytes big-endian)
            length_data = sock.recv(2)
            if len(length_data) != 2:
                continue
            msg_length = struct.unpack(">H", length_data)[0]
            
            # 3. Receive message content
            encoded_data = bytearray()
            while len(encoded_data) < msg_length * 4:
                chunk = sock.recv(msg_length * 4 - len(encoded_data))
                if not chunk:
                    break
                encoded_data.extend(chunk)
            
            if len(encoded_data) != msg_length * 4:
                continue
                
            # 4. Decode message (4 bytes -> 1 byte)
            decoded_bytes = bytearray()
            for i in range(0, len(encoded_data), 4):
                chunk = encoded_data[i:i+4]
                chunk = bytes(b for b in chunk if b != 0)
                decoded_bytes.extend(chunk)

            # 5. UTF-8 decoding
            try:
                msg = decoded_bytes.decode('utf-8')
            except UnicodeDecodeError:
                msg = decoded_bytes.decode('utf-8', errors='replace')
                print(f"Warning: Message contained invalid UTF-8 sequences")
            
            # 6. Message processing
            print(f"Received [{msg_type}]: {msg}")
            
            if msg_type == 't':
                htmlManager.addMessageBubble("User", msg)
                
            elif msg_type == 's':
                htmlManager.addMessageBubble("Server", msg)
                
                # Key extraction logic
                if "encode the text" in msg and encryption_type == "shift" and not key_found:
                    shift_key = extract_encryption_keys(msg)
                    key_found = True
                    next_server_msg = True
                    print(f"Shift key found: {shift_key}")

                elif "encode the text" in msg and encryption_type == "vigenere" and not key_found:
                    shift_key = extract_encryption_keys(msg)
                    key_found = True
                    next_server_msg = True
                    print(f"Shift key found: {shift_key}")

                elif "encode the text" in msg and encryption_type == "RSA" and not key_found:
                    shift_key = extract_encryption_keys(msg)
                    key_found = True
                    next_server_msg = True
                    print(f"N found: {shift_key[0]}, E found: {shift_key[1]}")
                
                elif "to send the hash" in msg and encryption_type == "hash":
                    key_found = True
                    next_server_msg = True

                # Message encryption handling
                elif next_server_msg and key_found:
                    msg_to_encrypt = msg
                    msg_found = True
                    print(f"Message to encrypt: {msg_to_encrypt}")
                    
                    if encryption_type == "shift":
                        try:
                            encrypted_msg = encrypt_shift(msg_to_encrypt, shift_key)
                            htmlManager.addMessageBubble("Shift encrypted", encrypted_msg.decode('utf-8', errors='replace'))
                            send(encrypted_msg, b'ISCs')
                        except Exception as e:
                            print(f"Error during shift encryption: {e}")
                            
                    elif encryption_type == "vigenere":
                        encrypted_msg = encrypt_vigenere(msg_to_encrypt, shift_key)
                        htmlManager.addMessageBubble("Vigenere encrypted", encrypted_msg.decode('utf-8', errors='replace'))
                        send(encrypted_msg, b'ISCs')
                        
                    elif encryption_type == "RSA":
                        encrypted_msg = encrypt_rsa(msg_to_encrypt, shift_key[0], shift_key[1])
                        htmlManager.addMessageBubble("RSA encrypted", encrypted_msg.decode('utf-8', errors='replace'))
                        send(encrypted_msg, b'ISCs')
                        
                    elif encryption_type == "hash":
                        hashed_msg = hash(msg_to_encrypt)
                        htmlManager.addMessageBubble("Hash", hashed_msg.decode('utf-8', errors='replace'))
                        send(hashed_msg, b'ISCs')
                    
                    # Reset flags
                    key_found = False
                    msg_found = False
                    next_server_msg = False
            
        except socket.timeout:
            continue
            
        except Exception as e:
            print(f"Critical receive error: {e}")
            pass
            
        sleep(0.1)

# =============================================
# GUI Event Handlers
# =============================================
def key_handler(event):
    """Handles Enter key press for message sending"""
    if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
        send_message()
    else:
        QLineEdit.keyPressEvent(entry_field, event)

def stop_listening():
    """Stops the receive_message thread"""
    global isRunning
    isRunning = False
    sleep(1)

def close_event(event):
    """Handles window close event"""
    event.accept()
    stop_listening()
    send("", b"ISCt")
    listening.join()

# =============================================
# GUI Initialization
# =============================================
try:
    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("ISC Secured Chat")
    window.setGeometry(100, 100, 800, 800)  # élargi à 800 pour laisser de la place au panneau de droite
    window.setWindowIcon(QIcon("img/isc-logo.png"))

    # Banner setup
    banner = QWidget()
    banner.setStyleSheet("background-color: #2c3e50;")
    banner_layout = QHBoxLayout(banner)

    # Sub-widget to group logo and text
    logo_text_widget = QWidget()
    logo_text_layout = QHBoxLayout(logo_text_widget)
    logo_text_layout.setContentsMargins(0, 0, 0, 0)
    logo_text_layout.setSpacing(10)

    logo_label = QLabel()
    logo_pixmap = QPixmap("img/isc-logo.png").scaled(50, 50, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
    logo_label.setPixmap(logo_pixmap)
    logo_text_layout.addWidget(logo_label)

    title_label = QLabel("ISC Secured Chat")
    title_label.setStyleSheet("""
        color: white;
        font-size: 20px;
        font-weight: bold;
    """)
    logo_text_layout.addWidget(title_label)

    banner_layout.addStretch()
    banner_layout.addWidget(logo_text_widget)
    banner_layout.addStretch()

    htmlManager = HtmlManager(window)

    entry_field = QLineEdit(window)
    entry_field.setPlaceholderText("Type your message here...")

    send_button = QPushButton(">", window)
    send_button.clicked.connect(send_message)

    # Key press handling
    entry_field.keyPressEvent = key_handler

    # --- New Right Panel ---
    right_panel = QWidget()
    right_layout = QVBoxLayout(right_panel)

    commands_label = QLabel("Server commands")
    commands_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
    right_layout.addWidget(commands_label)

    entry_field_encode = QLineEdit()
    entry_field_encode.setPlaceholderText("Enter a value here...")
    right_layout.addWidget(entry_field_encode)

    # Buttons for encryption methods
    def setServerCommand(command):
        if entry_field_encode.text() == "" and command != "hash":
            htmlManager.addMessageBubble("ISC Chat", "Please enter a value in the encryption field")
            return
        else:
            """Sets the server command based on the button clicked"""
            if command == "hash":
                entry_field.setText(f"/server task hash hash")
            else:
                entry_field.setText(f"/server task {command} encode  {entry_field_encode.text()}")
            send_message()
            entry_field_encode.setPlaceholderText("Enter a value here...")

    shift_button = QPushButton("Shift")
    shift_button.clicked.connect(lambda : setServerCommand("shift"))
    vigenere_button = QPushButton("Vigenère")
    vigenere_button.clicked.connect(lambda: setServerCommand("vigenere"))
    rsa_button = QPushButton("RSA")
    rsa_button.clicked.connect(lambda: setServerCommand("RSA"))
    hash_button = QPushButton("Hash")
    hash_button.clicked.connect(lambda: setServerCommand("hash"))

    

    right_layout.addWidget(shift_button)
    right_layout.addWidget(vigenere_button)
    right_layout.addWidget(rsa_button)
    right_layout.addWidget(hash_button)

    right_layout.addStretch()  # Push everything to the top

    # Layout setup
    gLayout = QGridLayout(window)
    gLayout.addWidget(banner, 0, 0, 1, 3)  # Banner on top across all columns
    gLayout.addWidget(htmlManager.chat_area, 1, 0, 1, 2)  # Chat area takes 2/3 width
    gLayout.addWidget(right_panel, 1, 2)  # Right panel in the third column
    gLayout.addWidget(entry_field, 2, 0, 1, 2)  # Input field spans 2 columns
    gLayout.addWidget(send_button, 2, 2)  # Send button under the right panel
    gLayout.setRowStretch(1, 1)  # Chat area and right panel expand
    gLayout.setRowStretch(2, 0)  # Input area does not expand
    gLayout.setColumnStretch(0, 3)  # Chat area column (left)
    gLayout.setColumnStretch(1, 1)  # Chat area column (right part if any)
    gLayout.setColumnStretch(2, 1)  # Right panel

    # Start message listening thread
    listening = Thread(target=receive_message)
    listening.daemon = True
    listening.start()

    window.setLayout(gLayout)
    window.closeEvent = close_event
    window.show()

    sys.exit(app.exec())

except Exception as e:
    print(f"An error occurred: {e}")

