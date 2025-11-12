import os
import bcrypt
import tkinter as tk
from tkinter import simpledialog, messagebox

masterHashFile = os.path.join(os.path.expanduser("~"), ".vaultMaster.hash")

def createMasterPassword(password: str):
    "Create and store master password"
    password = password.strip()
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    with open(masterHashFile, "wb") as f:
        f.write(hashed)
    print("Master password created")

def verifyMasterPassword(password: str) -> bool:
    "Check master password"
    password = password.strip()
    with open(masterHashFile, "rb") as f:
        storedHash = f.read()
    return bcrypt.checkpw(password.encode(), storedHash)

#Recovery Helper Functions
def loadRecovery():
    recoveryFile = os.path.join(os.path.expanduser("~"), ".vaultRecovery.txt")
    if os.path.exists(recoveryFile):
        with open(recoveryFile, "r", encoding="utf-8") as f:
            recoveryPassword = f.read().strip()
        return recoveryPassword
    return None

def saveRecovery(recoveryPassword: str):
    recoveryFile = os.path.join(os.path.expanduser("~"), ".vaultRecovery.txt")
    with open(recoveryFile, "w", encoding="utf-8") as f:
        f.write(recoveryPassword.strip())

def setRecoveryEmail(email: str):
    emailFile = os.path.join(os.path.expanduser("~"), ".vaultRecoveryEmail.txt")
    with open(emailFile, "w", encoding="utf-8") as f:
        f.write(email.strip())

def getMasterPassword(parent=None):
    "First time set up or Login verification"
    createdRoot = False
    if parent is None:
        parent = tk.Tk()
        createdRoot = True

    try:
        if not os.path.exists(masterHashFile):
            while True:
                pw = simpledialog.askstring("Create Master Password", "Enter a new master password:", show="*", parent=parent)
                if pw is None:
                    return None
                confirm = simpledialog.askstring("Confirm Password", "Confirm your master password:", show="*", parent=parent)

                if confirm is None:
                    if messagebox.askyesno("Cancel setup?", "cancel", parent=parent):
                        return None
                    else:
                        continue
                
                if pw != confirm:
                    messagebox.showerror("Mismatch", "Passwords do not match", parent=parent)
                    continue
                if pw.strip() == "":
                    messagebox.showerror("Invalid", "Password cannot have white space", parent=parent)
                    continue

                createMasterPassword(pw)
                messagebox.showinfo("Success", "Master password created", parent=parent)
                return pw
            
        else:
            attemptsLeft = 3
            while attemptsLeft > 0:
                pw = simpledialog.askstring("Master password", f"Enter password - attempts left {attemptsLeft}", show="*", parent=parent)
                if pw is None:
                    return None
                if verifyMasterPassword(pw):
                    return pw
                attemptsLeft -= 1
                continue
                
            messagebox.showerror("Access Denied", "incorrect password", parent=parent)
            return None
        
    finally:
        if createdRoot:
            parent.destroy()