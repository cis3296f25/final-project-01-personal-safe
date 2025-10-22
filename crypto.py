import os
import base64
from typing import Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


NONCE_SIZE = 12
KEY_SIZE = 32  # 32 Bytes -> 128 bits


class CryptoUtils:

    @staticmethod
    def generate_key() -> bytes:
        """Return a random AES-256 key"""
        return AESGCM.generate_key(bit_length=KEY_SIZE * 4)

    @staticmethod
    def encrypt(plaintext: str, key: bytes) -> str:
        """
        Encrypt plaintext with AES-GCM
        Returns a base64 string with nonce and cipher text
        """
        if len(key) not in (16, 24, 32):
            raise ValueError("key must be 16, 24, or 32 bytes")
        aesgcm = AESGCM(key)

        # A String only to be used once for increased security.
        nonce = os.urandom(NONCE_SIZE)

        # Creates the cipher tag
        ct = aesgcm.encrypt(nonce, plaintext.encode(), associated_data=None)
        return base64.b64encode(nonce + ct).decode()

    @staticmethod
    def decrypt(token_b64: str, key: bytes) -> str:
        """
        Decrypt a base64 token produced by encrypt()
        Returns the plaintext string
        """
        if len(key) not in (16, 24, 32):
            raise ValueError("key must be 16, 24, or 32 bytes")
        data = base64.b64decode(token_b64.encode())

        # Slice the data to obtain the nonce and cipher tag
        nonce, ct = data[:NONCE_SIZE], data[NONCE_SIZE:]

        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(nonce, ct, associated_data=None)
        return plaintext.decode()

    @staticmethod
    def derive_key(password: str, salt: bytes, iterations: int = 390000) -> bytes:
        """
        Derive a KEY_SIZE key from a password using PBKDF2-HMAC
        Returns raw bytes suitable for AESGCM
        """
        # Key Derivation Function
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=KEY_SIZE,
            salt=salt,
            iterations=iterations,
        )
        return kdf.derive(password.encode())

    @staticmethod
    def generate_salt(length: int = 16) -> bytes:
        """Return a random salt"""
        return os.urandom(length)
