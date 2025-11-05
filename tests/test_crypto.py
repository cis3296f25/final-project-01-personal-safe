import base64
import os
import pytest
import crypto
from crypto import CryptoUtils, NONCE_SIZE

def test_generate_key_length():
    key = CryptoUtils.generate_key()
    #should be 16, 24, or 32 bytes long
    assert isinstance(key, (bytes, bytearray))
    assert len(key) in (16, 24, 32)


def test_encrypt_decrypt_roundtrip():
    key = CryptoUtils.generate_key()
    plaintext = "this is a secret"
    token = CryptoUtils.encrypt(plaintext, key)
    assert isinstance(token, str)
    #must look like base64
    _ = base64.b64decode(token.encode())
    decrypted = CryptoUtils.decrypt(token, key)
    assert decrypted == plaintext


def test_encrypt_raises_with_invalid_key_length():
    bad_key = b"short"  # should not be 16/24/32 bytes
    with pytest.raises(ValueError):
        CryptoUtils.encrypt("x", bad_key)
    #decrypt should raise if key invalid
    #create valid token first using a valid key
    valid_key = CryptoUtils.generate_key()
    token = CryptoUtils.encrypt("hello", valid_key)
    with pytest.raises(ValueError):
        CryptoUtils.decrypt(token, bad_key)