import string
import pytest
from generate import generate_password

def test_password_length():
    pw = generate_password(12)
    assert len(pw) == 12
    pw2 = generate_password(20)
    assert len(pw2) == 20

def test_password_has_required_characters():
    pw = generate_password(12)
    #at least one lowercase
    assert any(c in string.ascii_lowercase for c in pw)
    #at least one uppercase
    assert any(c in string.ascii_uppercase for c in pw)
    #at least one digit
    assert any(c in string.digits for c in pw)
    #at least one symbol
    symbols = "!@#$%^&*()-_=+[]{}|;:,.<>?/"
    assert any(c in symbols for c in pw)

def test_password_too_short_raises():
    with pytest.raises(ValueError):
        generate_password(3)
