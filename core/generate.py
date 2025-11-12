import random
import string

def generate_password(length: int = 12) -> str:
    """
    Generate a random secure password.
    
    Default length is 12 characters. Includes:
    - Uppercase letters
    - Lowercase letters
    - Digits
    - Special characters
    """
    if length < 4:
        raise ValueError("Password length should be at least 4")

    letters_lower = string.ascii_lowercase
    letters_upper = string.ascii_uppercase
    digits = string.digits
    symbols = "!@#$%^&*()-_=+[]{}|;:,.<>?/"
    
    password = [
        random.choice(letters_lower),
        random.choice(letters_upper),
        random.choice(digits),
        random.choice(symbols)
    ]
    
    all_chars = letters_lower + letters_upper + digits + symbols
    password += [random.choice(all_chars) for _ in range(length - 4)]
    
    random.shuffle(password)
    return "".join(password)