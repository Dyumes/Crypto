import random
import hashlib



def hash(msg):
    data = msg
    hashed = hashlib.sha256(data.encode()).hexdigest()
    return "".join(hashed)



def encrypt_shift(msg, key):
    new_msg = ""
    for c in msg:
        new_msg += chr(ord(c)+int(key))
    return "".join(new_msg)

def generate_key_vig(msg: str, key: str) -> str:
    key = (key * (len(msg) // len(key) + 1))[:len(msg)]
    return key

def encrypt_vigenere(msg: str, key: str) -> str:
    encrypted_text = bytearray()
    key = generate_key_vig(msg, key)
    
    for i in range(len(msg)):
        encrypted_byte = (ord(msg[i]) + ord(key[i])) % 256  
        encrypted_text.append(encrypted_byte)
    
    return encrypted_text.decode("latin1")  


def decrypt_vigenere(msg, key):
    decrypted_text = []
    key = generate_key_vig(msg, key)
    for i in range(len(msg)):
        char = msg[i]
        if char.isupper():
            decrypted_char = chr((ord(char) - ord(key[i])) % 2**32)
        elif char.islower():
            decrypted_char = chr((ord(char) - ord(key[i])) % 2**32)
        else:
            decrypted_char = chr((ord(char) - ord(key[i])) % 2**32)
        decrypted_text.append(decrypted_char)
    return "".join(decrypted_text)



def generate_rsa_keys(n, e, bit_size=512):

    p = sympy.randprime(2**(bit_size//2 - 1), 2**(bit_size//2))  
    q = sympy.randprime(2**(bit_size//2 - 1), 2**(bit_size//2))  
    
    n = p * q 
    phi = (p - 1) * (q - 1)  

    e = 65537 
    d = pow(e, -1, phi)  

    return (n, e), (n, d)  


def encrypt_rsa(msg: str, n: int, e: int) -> str:
    """Chiffre un message RSA en traitant chaque byte séparément et renvoie une chaîne hexadécimale."""
    n = int(n)
    e = int(e)
    
    msg_bytes = msg.encode("utf-8")  # Convertir le message en bytes UTF-8
    cipher_ints = [pow(byte, e, n) for byte in msg_bytes]  # Chiffrement RSA par byte
    
    return "".join(f"{cipher:04x}" for cipher in cipher_ints)  # Retourne une chaîne hexadécimale

def decrypt_rsa(cipher_text: str, priv_key) -> str:
    """Déchiffre un message RSA stocké sous forme de chaîne hexadécimale."""
    n, d = priv_key

    msg_bytes = []
    
    for i in range(0, len(cipher_text), 4):  # Lire 4 caractères hexadécimaux à la fois
        cipher_int = int(cipher_text[i:i+4], 16)  # Convertir l'hex en int
        msg_byte = pow(cipher_int, d, n)  # Déchiffrement RSA
        msg_bytes.append(msg_byte)  # Stocker le byte déchiffré

    return bytes(msg_bytes).decode("utf-8", errors="ignore")  # Reconstruction du message original






#######################
#TEST
#######################

n = 3233  
e = 17    
d = 2753  
priv_key = (n, d)

message = "Hello, RSA!"
cipher_text = encrypt_rsa(message, n, e)
print("Chiffré (UTF-8) :", cipher_text)

decrypted = decrypt_rsa(cipher_text, priv_key)
print("Déchiffré :", decrypted)

crypt = ""

msg = "uilles séchées ont une valeur nutritive supérieure"
hashed = hash(msg)

