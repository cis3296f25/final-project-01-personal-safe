import tkinter as tk
from tkinter import simpledialog, messagebox
from vault import Vault


def build_ui(root: tk.Tk, vault: Vault) -> None:
    root.title("Password Manager Prototype")
    root.geometry("300x150")

    def add_password():
        site = simpledialog.askstring("Site", "Enter website/service name:")
        pwd = simpledialog.askstring("Password", "Enter password:")
        vault.add(site, pwd)
        if site and pwd:
            messagebox.showinfo("Saved", f"Password for {site} saved!")

    def view_passwords():
        output = "\n".join([f"{site}: {pwd}" for site, pwd in vault.items()])
        messagebox.showinfo("Vault", output or "Vault is empty.")

    tk.Button(root, text="Add Password", command=add_password).pack(pady=10)
    tk.Button(root, text="View Passwords", command=view_passwords).pack(pady=10)
