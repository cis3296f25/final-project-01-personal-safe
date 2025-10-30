import tkinter as tk
from tkinter import simpledialog, messagebox
from vault import Vault


def build_ui(root: tk.Tk, vault: Vault) -> None:
    root.title("Password Manager Prototype")
    root.geometry("300x300")

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
                listbox.delete(select[0])
                return
            #thoughts about catching an error here?
        tk.Button(win, text="Delete Selected", command=perform_delete).pack()
        tk.Button(win, text="Close", command=win.destroy).pack()

    def edit_password():
        sites = vault.get_sites()
        if not sites:
            messagebox.showinfo("Edit", "Vault is empty.")
            return
        
        win = tk.Toplevel(root)
        win.title("Edit Entry")
        win.geometry("300x250")
        win.transient(root)
        win.grab_set()

        tk.Label(win, text="Select site to update:").pack(pady=(8, 0))

        list_frame = tk.Frame(win)
        list_frame.pack(fill="both", expand=True, padx=8, pady=8)

        listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        listbox.configure(yscrollcommand=scrollbar.set)

        for s in sites:
            listbox.insert(tk.END, s)
    
        def perform_edit():
            select = listbox.curselection()
            if not select:
                messagebox.showwarning("Edit", "Select site please.")
                return
            site = listbox.get(select[0])

            #get current password (use vault.get if available, else scan items)
            current_pwd = None
            if hasattr(vault, "get"):
                try:
                    current_pwd = vault.get(site)
                except Exception:
                    current_pwd = None
            if current_pwd is None:
                #fallback method to use items to find the password
                items = dict(vault.items())
                current_pwd = items.get(site, "")

            #Ask for new password
            new_pwd = simpledialog.askstring("Edit Password", f"Enter new password for {site}:", initialvalue=current_pwd, parent=win)
            if new_pwd is None:
                return
            if new_pwd == "":
                messagebox.showwarning("Edit", "Password cannot be empty.")
                return
             #Save to vault: use update(), but fall back to add() if it fails
            try:
                if hasattr(vault, "update"):
                    ok = vault.update(site, new_pwd)
                    #allow update to return True/False or raise on error
                    if ok is False:
                        messagebox.showerror("Edit", f"Failed to update password for {site}.")
                        return
                else:
                    #fallback
                    vault.add(site, new_pwd)
            except Exception as e:
                messagebox.showerror("Edit", f"Error saving new password for {site}: {e}")
                return

            messagebox.showinfo("Edited", f"Password for {site} updated.")
            win.destroy()

        tk.Button(win, text="Edit Selected", command=perform_edit).pack()
        tk.Button(win, text="Close", command=win.destroy).pack()
        
    tk.Button(root, text="Add Password", command=add_password).pack(pady=8)
    tk.Button(root, text="View Passwords", command=view_passwords).pack(pady=8)
    tk.Button(root, text="Delete Password", command=delete_password).pack(pady=8)
    tk.Button(root, text="Edit Password", command=edit_password).pack(pady=8)    