import tkinter as tk
from vault import Vault
from ui import build_ui


def main():
    root = tk.Tk()
    vault = Vault()
    build_ui(root, vault)
    root.mainloop()


if __name__ == "__main__":
    main()
