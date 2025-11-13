import os
import ssl
import bcrypt
import tkinter as tk
import base64
import time
import smtplib
from email.message import EmailMessage
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



def storeTokenHash(token: str, ttl_seconds: int = 3600):
    token_bytes = token.encode()
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(token_bytes, salt)  # bytes
    b64 = base64.b64encode(hashed).decode()
    obj = loadRecovery()
    obj['token_hash_b64'] = b64
    obj['token_expiry'] = int(time.time()) + ttl_seconds
    obj['attempts_left'] = 3
    saveRecovery(obj)

def clearToken():
    obj = loadRecovery()
    obj.pop('token_hash_b64', None)
    obj.pop('token_expiry', None)
    obj['attempts_left'] = 3
    saveRecovery(obj)

def sendRecoveryEmail(smtpConfig: dict, toEmail: str, token: str) -> None:
    host = smtpConfig['host']
    port = smtpConfig.get('port', 465 if smtpConfig.get('use_ssl', True) else 587)
    username = smtpConfig.get('username')
    password = smtpConfig.get('password')
    use_ssl = smtpConfig.get('use_ssl', True)

    message = f"""Subject: Vault password reset token

You requested a password reset for your vault.
Use this one-time token to reset your master password (expires in 1 hour):

{token}

If you did not request this, ignore this email.
"""
    if use_ssl:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(host, port, context=context) as server:
            if username and password:
                server.login(username, password)
            server.sendmail(username or f"no-reply@{host}", toEmail, message)
    else:
        with smtplib.SMTP(host, port) as server:
            server.starttls(context=ssl.create_default_context())
            if username and password:
                server.login(username, password)
            server.sendmail(username or f"no-reply@{host}", toEmail, message)

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
                
                email = simpledialog.askstring("Recovery Email (optional)", "Enter recovery email (optional):", parent=parent)
                if email:
                    setRecoveryEmail(email)
                    messagebox.showinfo("Recovery", f"Recovery email {email} saved.", parent=parent)
            
                
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