
import socket
import struct
import time

SERVER_ADDRESS = "vlbelintrocrypto.hevs.ch"
SERVER_PORT = 6000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def connect():
    try:
        print("Trying to connect to the server...")
        sock.connect((SERVER_ADDRESS, SERVER_PORT))
        print("Connection successful")
    except Exception as e:
        print(f"Error: {e}")

def close():
    try:
        sock.close()
        print("\nConnection closed")
    except Exception as e:
        print(f"Error: {e}")

def send(msg, header):
    try:        
        length = struct.pack(">H", len(msg))
        encoded_message = msg
        if isinstance(msg, bytearray) == False:
            encoded_message = b"".join(struct.pack(">I", ord(c)) for c in msg)
        else:
            # encoded_message = b"".join(struct.pack(">I", b) for b in msg)
            encoded_message = b"".join(bytes([b]) for b in msg)
        full_message = header + length + encoded_message

        sock.send(full_message)
        print(f"\nEncoded msg : {encoded_message}")
        print(f"\nMessage sent: {msg}")

    except Exception as e:
        print(f"Error: {e}")

def listen():
    try:
        sock.settimeout(1)  # Timeout after 1 second
        sock.recv(3)
        type = sock.recv(1).decode()
        len = int.from_bytes(sock.recv(2), byteorder="big") * 4
        msg = sock.recv(len).decode(errors="ignore")
        return (type, msg.replace('\x00', ''))
    
    except socket.timeout:
        return None # Ignore timeout errors
    except socket.error as e:
        print(f"Error receiving data: {e}")

    return None
