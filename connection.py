import socket
import struct
import re

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
        encoded_message = b"".join(struct.pack(">I", ord(c)) for c in msg)

        full_message = header + length + encoded_message

        sock.send(full_message)
        print(f"\nMessage sent: {msg}")

    except Exception as e:
        print(f"Error: {e}")

def listen():
    try:
        sock.recv(3)
        type = sock.recv(1).decode()
        len = int.from_bytes(sock.recv(2), byteorder="big") * 4
        msg = sock.recv(len).decode()
        return (type, msg.replace('\x00', ''))

    except socket.error as e:
        print(f"Error receiving data: {e}")

    return None