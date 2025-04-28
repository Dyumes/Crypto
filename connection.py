import socket
import struct
from time import sleep
import base64

# =============================================
# Network Configuration Constants
# =============================================
SERVER_ADDRESS = "vlbelintrocrypto.hevs.ch"  # Server hostname
SERVER_PORT = 6000                          # Server port number

# Global socket instance
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# =============================================
# Connection Management Functions
# =============================================
def connect():
    """
    Establishes a TCP connection to the server.
    Handles connection errors gracefully.
    """
    try:
        print("Trying to connect to the server...")
        sock.connect((SERVER_ADDRESS, SERVER_PORT))
        print("Connection successful")
    except Exception as e:
        print(f"Error: {e}")

def close():
    """
    Closes the socket connection.
    Ensures proper cleanup of network resources.
    """
    try:
        sock.close()
        print("\nConnection closed")
    except Exception as e:
        print(f"Error: {e}")

# =============================================
# Data Transmission Functions
# =============================================
def send(msg, header):
    """
    Sends a message with a protocol header.
    
    Args:
        msg: The message to send (str or bytes)
        header: 4-byte protocol header (e.g., b'ISCt')
        
    Raises:
        ValueError: If header is invalid
        Exception: On network errors
    """
    try:
        # Strict header validation
        if not isinstance(header, bytes) or len(header) != 4:
            raise ValueError("Header must be exactly 4 bytes (e.g. b'ISCt')")
        
        # Message conversion handling
        if isinstance(msg, str):
            # UTF-8 encoding with 4-byte expansion
            utf8_encoded = msg.encode('utf-8')
            encoded_msg = bytearray()
            for byte in utf8_encoded:
                encoded_msg.extend(byte.to_bytes(4, 'big'))
            msg = encoded_msg
        
        # Calculate character length (not byte length)
        char_length = len(msg) // 4 if isinstance(msg, (bytes, bytearray)) else len(msg)
        length = struct.pack(">H", char_length)
        
        # Send the complete packet: [4-byte header][2-byte length][message]
        sock.send(header + length + msg)
        
    except Exception as e:
        print(f"Send failed: {e}")
        raise  # Re-raise exception for caller handling

# =============================================
# Data Reception Functions
# =============================================
def listen():
    """
    Listens for incoming messages from the server.
    
    Returns:
        tuple: (message_type, message_content) or None on timeout/error
    """
    try:
        # Configure socket timeout
        sock.settimeout(1)  # 1 second timeout
        
        # Receive protocol header (3 bytes) and message type (1 byte)
        sock.recv(3)  # Expected to be 'ISC'
        type = sock.recv(1).decode()  # Message type (t/s/i)
        
        # Receive message length (2 bytes big-endian)
        len = int.from_bytes(sock.recv(2), byteorder="big") * 4
        
        # Receive message content
        msg = sock.recv(len).decode(errors="ignore")
        
        # Clean null bytes and return
        return (type, msg.replace('\x00', ''))
    
    except socket.timeout:
        return None  # Silent timeout handling
    except socket.error as e:
        print(f"Error receiving data: {e}")
        return None