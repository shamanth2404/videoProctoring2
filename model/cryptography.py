# import random

# # Utility function to compute the modular inverse
# def mod_inverse(a, p):
#     return pow(a, -1, p)

# # Key Generation
# def elgamal_key_generation():
#     p = 1534899272561676244925313717014331740490094532609834959814346921905689869862264593212975473787189514436889176526473093615929993728061165964347353440008577  # Example prime number, should be large in real scenarios
#     d = 107  # Private key
#     e1 = 2  # Example primitive root, should be checked for being a primitive root in real scenarios
#     e2 = pow(e1, d, p)  # Public key component
#     public_key = (e1, e2, p)
#     private_key = d
#     return public_key, private_key

# # Encryption
# def elgamal_encryption(e1, e2, p, P):
#     r = 54513 # Random integer
#     C1 = pow(e1, r, p)  # C1 = e1^r mod p
#     C2 = (P * pow(e2, r, p)) % p  # C2 = P * e2^r mod p
#     return C1, C2

# # Decryption
# def elgamal_decryption(d, p, C1, C2):
#     s = pow(C1, d, p)  # s = C1^d mod p
#     s_inv = mod_inverse(s, p)  # s^-1 mod p
#     P = (C2 * s_inv) % p  # P = C2 * s^-1 mod p
#     return P

# # Example usage
# public_key, private_key = elgamal_key_generation()
# print("Public Key: ", public_key)
# print("Private Key: ", private_key)

# P = 2300  # Example plaintext
# C1, C2 = elgamal_encryption(public_key[0], public_key[1], public_key[2], P)
# print("Ciphertext: (C1, C2) = ", (C1, C2))

# decrypted_P = elgamal_decryption(private_key, public_key[2], C1, C2)
# print("Decrypted Plaintext: ", decrypted_P)

import tkinter as tk
from tkinter import messagebox

# Utility function to compute the modular inverse
def mod_inverse(a, p):
    return pow(a, -1, p)

# Key Generation
def elgamal_key_generation(p, d, e1):
    e2 = pow(e1, d, p)  # Public key component
    public_key = (e1, e2, p)
    private_key = d
    return public_key, private_key

# Encryption
def elgamal_encryption(e1, e2, p, P, r):
    C1 = pow(e1, r, p)  # C1 = e1^r mod p
    C2 = (P * pow(e2, r, p)) % p  # C2 = P * e2^r mod p
    return C1, C2

# Decryption
def elgamal_decryption(d, p, C1, C2):
    s = pow(C1, d, p)  # s = C1^d mod p
    s_inv = mod_inverse(s, p)  # s^-1 mod p
    P = (C2 * s_inv) % p  # P = C2 * s^-1 mod p
    return P

def generate_keys():
    try:
        p = int(entry_p.get())
        d = int(entry_d.get())
        e1 = int(entry_e1.get())
        public_key, private_key = elgamal_key_generation(p, d, e1)
        text_public_key.delete(1.0, tk.END)
        text_public_key.insert(tk.END, f"Public Key: {public_key}")
        text_private_key.delete(1.0, tk.END)
        text_private_key.insert(tk.END, f"Private Key: {private_key}")
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid integers for p, d, and e1.")

def encrypt_message():
    try:
        P = int(entry_plaintext.get())
        r = int(entry_r.get())
        e1, e2, p = map(int, text_public_key.get(1.0, tk.END).strip().split(':')[1].strip(' ()').split(','))
        C1, C2 = elgamal_encryption(e1, e2, p, P, r)
        text_ciphertext.delete(1.0, tk.END)
        text_ciphertext.insert(tk.END, f"Ciphertext: (C1: {C1}, C2: {C2})")
        entry_ciphertext1.delete(0, tk.END)
        entry_ciphertext1.insert(0, str(C1))
        entry_ciphertext2.delete(0, tk.END)
        entry_ciphertext2.insert(0, str(C2))
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid integers for the plaintext and r.")

def decrypt_message():
    try:
        d = int(entry_d.get())
        p = int(entry_p.get())
        C1 = int(entry_ciphertext1.get())
        C2 = int(entry_ciphertext2.get())        
        decrypted_P = elgamal_decryption(d, p, C1, C2)
        label_decrypted.config(text=f"Decrypted Plaintext: {decrypted_P}")
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid integers for the ciphertext components.")

# Creating main window
root = tk.Tk()
root.title("ElGamal Encryption/Decryption")

# Frames for Alice and Bob
frame_alice = tk.Frame(root, padx=20, pady=20)
frame_alice.grid(row=0, column=0, sticky="n")

frame_bob = tk.Frame(root, padx=20, pady=20)
frame_bob.grid(row=0, column=1, sticky="n")

# Alice's Side
label_alice = tk.Label(frame_alice, text="Alice", font=("Arial", 16))
label_alice.grid(row=0, column=0, columnspan=2)

label_plaintext = tk.Label(frame_alice, text="Plaintext P:")
label_plaintext.grid(row=1, column=0)
entry_plaintext = tk.Entry(frame_alice)
entry_plaintext.grid(row=1, column=1)

label_r = tk.Label(frame_alice, text="Random integer r:")
label_r.grid(row=2, column=0)
entry_r = tk.Entry(frame_alice)
entry_r.grid(row=2, column=1)

button_encrypt = tk.Button(frame_alice, text="Encrypt", command=encrypt_message)
button_encrypt.grid(row=3, column=0, columnspan=2, pady=10)

label_ciphertext = tk.Label(frame_alice, text="Ciphertext: (C1, C2)")
label_ciphertext.grid(row=4, column=0, columnspan=2)

scrollbar_ciphertext = tk.Scrollbar(frame_alice)
scrollbar_ciphertext.grid(row=5, column=2, sticky='ns')

text_ciphertext = tk.Text(frame_alice, height=4, width=40, yscrollcommand=scrollbar_ciphertext.set)
text_ciphertext.grid(row=5, column=0, columnspan=2)
scrollbar_ciphertext.config(command=text_ciphertext.yview)

# Bob's Side
label_bob = tk.Label(frame_bob, text="Bob", font=("Arial", 16))
label_bob.grid(row=0, column=0, columnspan=2)

label_p = tk.Label(frame_bob, text="Prime number p:")
label_p.grid(row=1, column=0)
entry_p = tk.Entry(frame_bob)
entry_p.grid(row=1, column=1)

label_d = tk.Label(frame_bob, text="Private key d:")
label_d.grid(row=2, column=0)
entry_d = tk.Entry(frame_bob)
entry_d.grid(row=2, column=1)

label_e1 = tk.Label(frame_bob, text="Primitive root e1:")
label_e1.grid(row=3, column=0)
entry_e1 = tk.Entry(frame_bob)
entry_e1.grid(row=3, column=1)

button_generate_keys = tk.Button(frame_bob, text="Generate Keys", command=generate_keys)
button_generate_keys.grid(row=4, column=0, columnspan=2, pady=10)

label_public_key = tk.Label(frame_bob, text="Public Key: ")
label_public_key.grid(row=5, column=0, columnspan=2)

scrollbar_public_key = tk.Scrollbar(frame_bob)
scrollbar_public_key.grid(row=6, column=2, sticky='ns')

text_public_key = tk.Text(frame_bob, height=4, width=40, yscrollcommand=scrollbar_public_key.set)
text_public_key.grid(row=6, column=0, columnspan=2)
scrollbar_public_key.config(command=text_public_key.yview)

label_private_key = tk.Label(frame_bob, text="Private Key: ")
label_private_key.grid(row=7, column=0, columnspan=2)

scrollbar_private_key = tk.Scrollbar(frame_bob)
scrollbar_private_key.grid(row=8, column=2, sticky='ns')

text_private_key = tk.Text(frame_bob, height=4, width=40, yscrollcommand=scrollbar_private_key.set)
text_private_key.grid(row=8, column=0, columnspan=2)
scrollbar_private_key.config(command=text_private_key.yview)

label_ciphertext1 = tk.Label(frame_bob, text="Ciphertext C1:")
label_ciphertext1.grid(row=9, column=0)
entry_ciphertext1 = tk.Entry(frame_bob)
entry_ciphertext1.grid(row=9, column=1)

label_ciphertext2 = tk.Label(frame_bob, text="Ciphertext C2:")
label_ciphertext2.grid(row=10, column=0)
entry_ciphertext2 = tk.Entry(frame_bob)
entry_ciphertext2.grid(row=10, column=1)

button_decrypt = tk.Button(frame_bob, text="Decrypt", command=decrypt_message)
button_decrypt.grid(row=11, column=0, columnspan=2, pady=10)

label_decrypted = tk.Label(frame_bob, text="Decrypted Plaintext: ")
label_decrypted.grid(row=12, column=0, columnspan=2)

# Run the application
root.mainloop()
