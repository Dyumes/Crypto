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


#######################
#TEST
#######################

"""""""""""
text_to_encrypt = "abcdefghijklmnopqrstuvwxyzéà$è¨,.-<12345678890+*ç%&/()=?"

key = "cywjAM3I1"

encrypted_text = encrypt_vigenere(text_to_encrypt, key)

print(f"Encrypted text: {encrypted_text}")

decrypted_text = decrypt_vigenere(encrypted_text, key)

print(f"Decrypted text : {decrypted_text}")

msg = "abcdefghijklmnopqrstuvwxyz1234567890+*ç%&/()=ü!ä£"
key = 12

encoded = encrypt_shift(msg, 12)

print(encoded)
"""
