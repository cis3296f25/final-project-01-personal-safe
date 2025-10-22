import tkinter as tk
from vault import Vault
from ui import build_ui
from masterPassword import getMasterPassword


def main():
    root = tk.Tk()

    pw = getMasterPassword(parent=root)
    if not pw:
        root.destroy()
        return

    vault = Vault(pw)
    build_ui(root, vault)
    root.mainloop()


if __name__ == "__main__":
    main()
