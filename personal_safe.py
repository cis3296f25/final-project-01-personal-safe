import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import base64


KEY = 42 

def encrypt(data: str) -> str:
    return base64.b64encode(bytes([c ^ KEY for c in data.encode()])).decode()

def decrypt(data: str) -> str:
    return ''.join([chr(c ^ KEY) for c in base64.b64decode(data.encode())])

VAULT_FILE = "vault.json"

def save_vault(vault):
    encrypted = encrypt(json.dumps(vault))
    with open(VAULT_FILE, "w") as f:
        f.write(encrypted)

def load_vault():
    try:
        with open(VAULT_FILE, "r") as f:
            encrypted = f.read()
        data = decrypt(encrypted)
        return json.loads(data)
    except FileNotFoundError:
        return {}

vault = load_vault()

def add_password():
    site = simpledialog.askstring("Site", "Enter website/service name:")
    pwd = simpledialog.askstring("Password", "Enter password:")
    if site and pwd:
        vault[site] = pwd
        save_vault(vault)
        messagebox.showinfo("Saved", f"Password for {site} saved!")

def view_passwords():
    output = "\n".join([f"{site}: {pwd}" for site, pwd in vault.items()])
    messagebox.showinfo("Vault", output or "Vault is empty.")

root = tk.Tk()
root.title("Password Manager Prototype")
root.geometry("300x150")

tk.Button(root, text="Add Password", command=add_password).pack(pady=10)
tk.Button(root, text="View Passwords", command=view_passwords).pack(pady=10)

root.mainloop()