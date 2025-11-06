import tkinter as tk
from tkinter import simpledialog, messagebox
from vault import Vault
from generate import generate_password


def build_ui(root: tk.Tk, vault: Vault) -> None:
    root.title("Password Manager Prototype")
    root.geometry("300x300")

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

    def copy_to_clipboard(text: str, root: tk.Tk):
        try:
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()
        except Exception:
            return False

    def view_passwords():
        items = vault.items()
        if not items:
            messagebox.showinfo("Vault", "Vault is empty.")
            return
        #output = "\n".join([f"{site}: {pwd}" for site, pwd in vault.items()])
        #messagebox.showinfo("Vault", output or "Vault is empty.")

        #new window
        win = tk.Toplevel(root)
        win.title("Vault")
        win.geometry("400x300")
        win.transient(root)
        win.grab_set()

        tk.Label(win, text="Saved Entries:").pack(pady=(8, 0))

        #listbox n scrollbar. upgrading the ui a bit
        frame = tk.Frame(win)
        frame.pack(fill="both", expand=True, padx=8, pady=8)

        listbox = tk.Listbox(frame, selectmode=tk.SINGLE)
        listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame, orient="vertical", command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        listbox.configure(yscrollcommand=scrollbar.set)

        for site, _ in items:
            listbox.insert(tk.END, site)

        #new password display
        details_frame = tk.Frame(win)
        details_frame.pack(fill="x", padx=8, pady=(0, 8))

        tk.Label(details_frame, text="Password:").grid(row=0, column=0, sticky="w")
        pwd_var = tk.StringVar(value="")
        masked_var = tk.BooleanVar(value=True)

        pwd_entry = tk.Entry(details_frame, textvariable=pwd_var, state="readonly", width=35)
        pwd_entry.grid(row=0, column=1, padx=(6, 0))

        def refresh_selected(_evt=None):
            sel = listbox.curselection()
            if not sel:
                pwd_var.set("")
                return
            site = listbox.get(sel[0])
            try:
                pwd = vault.get(site)
            except Exception:
                pwd = dict(vault.items()).get(site, "")
            pwd_var.set("*" * len(pwd) if masked_var.get() else pwd)

        listbox.bind("<<ListboxSelect>>", refresh_selected)

        def toggle_show():
            masked_var.set(not masked_var.get())
            refresh_selected()
        #copy function
        def copy_selected():
            sel = listbox.curselection()
            if not sel:
                messagebox.showwarning("Copy", "Select a site first.")
                return
            site = listbox.get(sel[0])
            try:
                pwd = vault.get(site)
            except Exception:
                pwd = dict(vault.items()).get(site, "")
            if not pwd:
                messagebox.showwarning("Copy", "No password found")
                return
            success = copy_to_clipboard(pwd, root)
            if success:
                messagebox.showinfo("Copied", f"Password for {site} copied to clipboard.")
            else:
                messagebox.showerror("Copy", "Failed to copy to clipboard.")

        btn_frame = tk.Frame(win)
        btn_frame.pack(fill="x", padx=8, pady=(0, 8))

        tk.Button(btn_frame, text="Show / Hide", command=toggle_show).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Copy", command=copy_selected).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Close", command=win.destroy).pack(side="right", padx=4)

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

            current_pwd = None
            if hasattr(vault, "get"):
                try:
                    current_pwd = vault.get(site)
                except Exception:
                    current_pwd = None
            if current_pwd is None:
                items = dict(vault.items())
                current_pwd = items.get(site, "")

            new_pwd = simpledialog.askstring("Edit Password", f"Enter new password for {site}:", initialvalue=current_pwd, parent=win)
            if new_pwd is None:
                return
            if new_pwd == "":
                messagebox.showwarning("Edit", "Password cannot be empty.")
                return
            try:
                if hasattr(vault, "update"):
                    ok = vault.update(site, new_pwd)
                    if ok is False:
                        messagebox.showerror("Edit", f"Failed to update password for {site}.")
                        return
                else:
                    vault.add(site, new_pwd)
            except Exception as e:
                messagebox.showerror("Edit", f"Error saving new password for {site}: {e}")
                return

            messagebox.showinfo("Edited", f"Password for {site} updated.")
            win.destroy()

        tk.Button(win, text="Edit Selected", command=perform_edit).pack()
        tk.Button(win, text="Close", command=win.destroy).pack()
        
    tk.Button(root, text="Add Password", command=add_password).pack(pady=10)
    tk.Button(root, text="View Passwords", command=view_passwords).pack(pady=10)
    tk.Button(root, text="Delete Password", command=delete_password).pack(pady=10)
    tk.Button(root, text="Edit Password", command=edit_password).pack(pady=10) 
