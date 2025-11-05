import vault

def test_vault_initial_load():
    v = vault.Vault(master_password="test123")
    assert v.is_empty() is True

def test_add_and_items():
    v = vault.Vault(master_password="pass")
    v._data = {}
    v.add("github.com", "meow123")
    assert ("github.com", "meow123") in v.items()

def test_add_ignores_empty_inputs():
    v = vault.Vault(master_password="pass")
    v._data = {}
    v.add("", "somepwd")
    v.add("google.com", "")
    assert v.is_empty()

def test_get_sites_and_get():
    v = vault.Vault(master_password="pass")
    v._data = {"discord": "abc123"}
    assert v.get_sites() == ["discord"]
    assert v.get("discord") == "abc123"
    assert v.get("unknown") is None

def test_delete_existing_and_missing_site():
    v = vault.Vault(master_password="pass")
    v._data = {"spotify": "music!"}
    deleted = v.delete("spotify")
    assert deleted is True
    assert v._data == {}
    deleted_again = v.delete("spotify")
    assert deleted_again is False