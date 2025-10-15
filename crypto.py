import base64

KEY = 42


def encrypt(data: str) -> str:
    return base64.b64encode(bytes([c ^ KEY for c in data.encode()])).decode()


def decrypt(data: str) -> str:
    return "".join([chr(c ^ KEY) for c in base64.b64decode(data.encode())])
