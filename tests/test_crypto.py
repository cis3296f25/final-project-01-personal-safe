import crypto

def test_encrypt_decrypt_cycle():
    data = "mypassword123"
    key = "secretkey"
    encrypted = crypto.encrypt(data, key)
    decrypted = crypto.decrypt(encrypted, key)
    assert decrypted == data