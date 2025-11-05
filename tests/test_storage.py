import json
import pytest
from storage import save_vault, load_vault

def test_save_and_load_vault(tmp_path):
    vault_file = tmp_path / "vault.json"
    vault_data = {"github.com": "meow123", "discord": "abc123"}
    master_password = "TestPass123"

    save_vault(vault_data, master_password, vault_file=str(vault_file))

    assert vault_file.exists()

    loaded_data = load_vault(master_password, vault_file=str(vault_file))
    assert loaded_data == vault_data

def test_load_nonexistent_file(tmp_path):
    vault_file = tmp_path / "does_not_exist.json"
    loaded_data = load_vault("any_password", vault_file=str(vault_file))
    assert loaded_data == {}
