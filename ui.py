import tkinter as tk
from tkinter import simpledialog, messagebox
from vault import Vault


def build_ui(root: tk.Tk, vault: Vault) -> None:
    root.title("Password Manager Prototype")
    root.geometry("300x150")

    def add_password():
        site = simpledialog.askstring("Site", "Enter website/service name:")
        if site is None:
            return
        pwd = simpledialog.askstring("Password", "Enter password:")
        if pwd is None:
            return
        vault.add(site, pwd)
        if site and pwd:
            messagebox.showinfo("Saved", f"Password for {site} saved!")

    def view_passwords():
        items = vault.items()
        if not items:
            messagebox.showinfo("Vault", "Vault is empty.")
            return
        output = "\n".join([f"{site}: {pwd}" for site, pwd in vault.items()])
        messagebox.showinfo("Vault", output or "Vault is empty.")

    def delete_password():
        sites = vault.get_sites()
        if not sites:
            messagebox.showinfo("Delete", "Vault is empty.")
            return
    
    def perform_delete():
        select = listbox.curselection()
        if not select:
            messagebox.showwarning("Delete", "Select site please.")
            return
        site = listbox.get(select[0])
        confirm = messagebox.askyesno("Confirm Delete", f"Delete password for {site}?")
        if not confirm:
            return
        deleted = vault.delete(site)
        if deleted:
            messagebox.showinfo("Deleted", f"Deleted entry for {site}.")
            #this is where it actually removes it
            listbox.delete(select[0])
            return
        #should we catch an error here?

#create pop up window using listbox?

    tk.Button(root, text="Add Password", command=add_password).pack(pady=10)
    tk.Button(root, text="View Passwords", command=view_passwords).pack(pady=10)
    tk.Button(root, text="Delete Password", command=delete_password).pack(pady=10)
