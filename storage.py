import json
import base64
import os
from typing import Dict, Optional
from crypto import CryptoUtils


VAULT_FILE = "vault.json"


def save_vault(
    vault: Dict[str, str], master_password: str, vault_file: Optional[str] = None
) -> None:
    """
    Save the vault to disk. File format:
      line1: base64(salt)
      line2: base64(ciphertext)

    We derive the encryption key from the provided master_password and a new random salt.
    """
    path = vault_file or VAULT_FILE

    salt = CryptoUtils.generate_salt()
    key = CryptoUtils.derive_key(master_password, salt)

    # encrypt the JSON payload
    plaintext = json.dumps(vault)
    ciphertext = CryptoUtils.encrypt(plaintext, key)

    header = base64.b64encode(salt).decode()
    with open(path, "w") as f:
        f.write(header + "\n" + ciphertext)


def load_vault(
    master_password: str, vault_file: Optional[str] = None
) -> Dict[str, str]:
    """
    Load the vault using master_password to derive the key from the salt stored in the first line.
    Backwards-compatible: if file doesn't contain a header, attempt to decrypt the whole file with
    a key derived from the provided password and a default salt (will likely fail).
    """
    path = vault_file or VAULT_FILE
    try:
        with open(path, "r") as f:
            lines = f.read().splitlines()

        if not lines:
            return {}

        # If file has at least 2 lines, assume first line is base64 salt and second+ is cipher text
        try:
            salt = base64.b64decode(lines[0])
            ciphertext = "\n".join(lines[1:])
            key = CryptoUtils.derive_key(master_password, salt)
            plaintext = CryptoUtils.decrypt(ciphertext, key)
            return json.loads(plaintext)
        except Exception:
            pass
    except FileNotFoundError:
        return {}
