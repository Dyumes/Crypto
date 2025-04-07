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

    ##while 

    return (n, e), (n, d)  



def encrypt_rsa(msg: str, n: int, e: int) -> str:
    result = bytearray()
    for c in msg:
        result.extend(
            int.to_bytes(
                pow(int.from_bytes(c.encode()), int(e), int(n))
                , 4
            )
        )

    
    return result




#######################
#TEST
#######################



