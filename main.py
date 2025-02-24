import socket
import struct

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

def send(msg):
    try:
        header = b"ISCt"
        length = struct.pack(">H", len(msg))
        encoded_message = b"".join(struct.pack(">I", ord(c)) for c in msg)

        full_message = header + length + encoded_message

        sock.send(full_message)
        print(f"\nMessage sent: {msg}")

        response = sock.recv(1024)
        print(f"Server's response: {response}")

    except Exception as e:
        print(f"Error: {e}")

def listen():
    try:
        data = sock.recv(1024)
        print(f"Received: {data.decode()}")

    except socket.error as e:
        print(f"Error receiving data: {e}")

print("ChatApp - TEST")
connect()
while(1):
    listen()
    message = input("Please enter a new message : ")
    if message != "/q":
        send(message)
    else:
        close()
        break
