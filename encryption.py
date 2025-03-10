def encrypt_shift(msg, key):
    new_msg = ""
    for c in msg:
        new_msg += chr(ord(c)+int(key))
    return "".join(new_msg)

def encrypt_vigenere(msg, key):
    encrypted_text = []
    for i in range(len(msg)):
        char = msg[i]
        if char.isupper():
            encrypted_char = chr((ord(char) + ord(key[i]) - 2 * ord('A')) % 26 + ord('A'))
        elif char.islower():
            encrypted_char = chr((ord(char) + ord(key[i]) - 2 * ord('a')) % 26 + ord('a'))
        else:
            encrypted_char = char
        encrypted_text.append(encrypted_char)
    return "".join(encrypted_text)

def decrypt_vigenere(msg, key):
    decrypted_text = []
    for i in range(len(msg)):
        char = msg[i]
        if char.isupper():
            decrypted_char = chr((ord(char) - ord(key[i]) + 26) % 26 + ord('A'))
        elif char.islower():
            decrypted_char = chr((ord(char) - ord(key[i]) + 26) % 26 + ord('a'))
        else:
            decrypted_char = char
        decrypted_text.append(decrypted_char)
    return "".join(decrypted_text)

# text_to_encrypt = "abcdefghijklmnopqrstuvwxyz 0123456789 ¨è$àé-.,<"

# key = "TEST"

# encrypted_text = encrypt_vigenere(text_to_encrypt, key)

# print(f"Encrypted text: {encrypted_text}")

# decrypted_text = decrypt_vigenere(encrypted_text, key)

# print(f"Decrypted text : {decrypted_text}")