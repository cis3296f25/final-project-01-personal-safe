import json
from typing import Dict
from crypto import encrypt, decrypt

VAULT_FILE = "vault.json"


def save_vault(vault: Dict[str, str]) -> None:
    encrypted = encrypt(json.dumps(vault))
    with open(VAULT_FILE, "w") as f:
        f.write(encrypted)


def load_vault() -> Dict[str, str]:
    try:
        with open(VAULT_FILE, "r") as f:
            encrypted = f.read()
        data = decrypt(encrypted)
        return json.loads(data)
    except FileNotFoundError:
        return {}
