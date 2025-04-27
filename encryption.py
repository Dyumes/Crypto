import random
import hashlib
from sympy import isprime, primitive_root, nextprime, randprime


#""""""""""""""""""""""""""""""""""
#  Encryption Functions
#""""""""""""""""""""""""""""""""""

def encrypt_shift(msg, key):
    """
    Encrypt a message using a simple shift cipher.

    Parameters:
        msg (str): The message to encrypt.
        key (int): The shift value to apply to each character.

    Returns:
        bytearray: The encrypted message as a bytearray.
        
    Explanation:
        For each character in the message:
        - The character is converted to its Unicode code point.
        - The shift is applied to the code point.
        - The shifted code point is converted back to bytes and stored as a 4-byte representation.
    """
    result = bytearray()
    
    # For each character in the message
    for c in msg:
        # Convert the character to bytes
        result.extend(int.to_bytes(int.from_bytes(c.encode()), 4))
        
        # Apply the shift to the byte representation and update the last 4 bytes
        result[-4:] = int.to_bytes(int.from_bytes(c.encode()) + key, 4)
    
    return result


def encrypt_vigenere(msg, key):
    """
    Encrypt a message using the Vigenère cipher.

    Parameters:
        msg (str): The message to encrypt.
        key (str): The key used for the Vigenère cipher, a string.

    Returns:
        bytearray: The encrypted message as a bytearray.

    Explanation:
        For each character in the message:
        - The character is converted to its Unicode code point.
        - The corresponding character in the key is used to modify the character.
        - The shifted code point is converted back to bytes and stored as a 4-byte representation.
    """
    result = bytearray()

    # For each character in the message, apply Vigenère shift based on the key
    for i, c in enumerate(msg):
        # Convert the message character and the key character to integer byte representations
        intChar = int.from_bytes(c.encode())
        intKey = int.from_bytes(key[i % len(key)].encode())
        
        # Add the shifted value of the character and key, then convert back to 4 bytes
        result.extend(int.to_bytes((intChar + intKey), 4))
    
    return result


def encrypt_rsa(msg: str, n: int, e: int) -> str:
    """
    Encrypt a message using RSA encryption.

    Parameters:
        msg (str): The message to encrypt.
        n (int): The RSA modulus (part of the public key).
        e (int): The RSA exponent (part of the public key).

    Returns:
        bytearray: The encrypted message as a bytearray.

    Explanation:
        For each character in the message:
        - The character is converted to its integer value.
        - The RSA encryption is applied using the formula (m^e) % n.
        - The encrypted result is converted back to bytes and stored as a 4-byte representation.
    """
    result = bytearray()

    # For each character, apply RSA encryption
    for c in msg:
        result.extend(
            int.to_bytes(
                pow(int.from_bytes(c.encode()), int(e), int(n)), 4  # Apply RSA encryption formula
            )
        )
    
    return result

#""""""""""""""""""""""""""""""""""
#  Hashing Functions
#""""""""""""""""""""""""""""""""""

def hash(msg):
    """
    Generate a SHA-256 hash of a message and encode each character of the hash into 4 bytes.

    Parameters:
        msg (str): The message to hash.

    Returns:
        bytearray: The hashed message, encoded as a 4-byte sequence.

    Explanation:
        - The message is hashed using SHA-256 to produce a hexadecimal string.
        - Each character of the hexadecimal hash is then converted to a numeric value.
        - The numeric value is extended into a 4-byte big-endian representation.
    """
    data = msg
    hashed = hashlib.sha256(data.encode()).hexdigest()  # Generate hexadecimal SHA-256 hash
    encrypted = bytearray()

    # For each character in the hexadecimal hash, convert it to a byte
    for char in hashed:
        # Convert each hexadecimal character to its numeric value
        byte_val = ord(char)
        
        # Extend the numeric value into a 4-byte big-endian representation
        encrypted.extend(byte_val.to_bytes(4, 'big'))

    return encrypted


def hashVerify(msg, hash):
    """
    Verify the hash of a message by comparing it to the provided hash.

    Parameters:
        msg (str): The message to verify.
        hash (bytearray): The expected hash value to compare with.

    Returns:
        str: "true" if the hashes match, "false" otherwise.

    Explanation:
        - The message is hashed using SHA-256.
        - The result is compared with the provided hash.
        - A message is printed indicating whether the hashes match.
    """
    data = msg
    result = ""
    hashed = hashlib.sha256(data.encode()).hexdigest()  # Generate the hexadecimal hash
    
    if hashed == hash:
        print("Hash corresponding")
        result = "true"
    else:
        print("Hash not corresponding")
        result = "false"
    
    return result

#""""""""""""""""""""""""""""""""""
#  Diffie-Hellman Key Exchange
#""""""""""""""""""""""""""""""""""

def generate_difhel():
    """
    Generate Diffie-Hellman parameters for secure key exchange.

    Returns:
        tuple: A tuple (p, g), where:
            - p is a prime number used in the Diffie-Hellman protocol.
            - g is a primitive root modulo p.

    Explanation:
        - A prime number p is selected from a range.
        - A primitive root g modulo p is generated.
        - These values are used for key exchange in cryptographic protocols.
    """
    p = nextprime(random.randint(1000, 5000))  # Find a prime number greater than 1000
    while not isprime(p):  # Ensure p is prime
        p = nextprime(random.randint(1000, 5000))
    
    g = primitive_root(p)  # Find a primitive root modulo p
    return (p, g)




def secret_difhel(p, g, gB):
    """
    Compute the Diffie-Hellman shared secret for Alice using her private key and the received public value (gB).

    Parameters:
        p (int): The prime number from the Diffie-Hellman key exchange.
        g (int): The primitive root modulo p.
        gB (int): Bob's public key, used to compute the shared secret.

    Returns:
        tuple: A tuple (gA, shared_secret), where:
            - gA is Alice's public key.
            - shared_secret is the computed shared secret.

    Explanation:
        - Alice generates a private key a and computes her public key gA.
        - Alice then computes the shared secret using Bob's public key gB and her private key.
    """
    a = random.randint(2, int(p) - 2)  # Generate Alice's private key (a)
    gA = pow(int(g), a, int(p))  # Compute Alice's public key (gA)
    
    # Compute the shared secret using Bob's public key (gB) and Alice's private key (a)
    shared_secret = pow(int(gB), a, int(p))  
    return (gA, shared_secret)
