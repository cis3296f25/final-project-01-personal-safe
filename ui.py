import tkinter as tk
from tkinter import simpledialog, messagebox
from vault import Vault
from generate import generate_password


def build_ui(root: tk.Tk, vault: Vault) -> None:
    root.title("Password Manager Prototype")
    root.geometry("300x150")

    def add_password():
        site = simpledialog.askstring("Site", "Enter website/service name:")
        if site is None:
            return

        use_generated = messagebox.askyesno("Generate Password?", "Generate a random password?")

        if use_generated:
            pwd = generate_password()
            messagebox.showinfo("Generated Password", f"Generated password for {site}:\n\n{pwd}")
        else:
            pwd = simpledialog.askstring("Password", "Enter password:")
            if pwd is None:
                return

        vault.add(site, pwd)
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
        #create pop up window using listbox
        win = tk.Toplevel(root)
        win.title("Delete Entry")
        win.geometry("300x250")
        win.transient(root)
        win.grab_set()

        tk.Label(win, text="Select site to delete:").pack(pady=(8, 0))

        list_frame = tk.Frame(win)
        list_frame.pack(fill="both", expand=True, padx=8, pady=8)

        listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        listbox.configure(yscrollcommand=scrollbar.set)

        for s in sites:
            listbox.insert(tk.END, s)

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
            #thoughts about catching an error here?
        tk.Button(win, text="Delete Selected", command=perform_delete).pack()
        tk.Button(win, text="Close", command=win.destroy).pack()

    tk.Button(root, text="Add Password", command=add_password).pack(pady=10)
    tk.Button(root, text="View Passwords", command=view_passwords).pack(pady=10)
    tk.Button(root, text="Delete Password", command=delete_password).pack(pady=10)