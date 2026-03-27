from cryptography.fernet import Fernet


def generate_key() -> str:
    """Generate a new Fernet encryption key as a URL-safe base64 string."""
    return Fernet.generate_key().decode()


def encrypt(plaintext: str, key: str) -> str:
    """Encrypt a plaintext string using Fernet symmetric encryption.

    Args:
        plaintext: The string to encrypt.
        key: A URL-safe base64-encoded 32-byte key.

    Returns the encrypted token as a string.
    """
    fernet = Fernet(key.encode())
    return fernet.encrypt(plaintext.encode()).decode()


def decrypt(token: str, key: str) -> str:
    """Decrypt a Fernet-encrypted token.

    Args:
        token: The encrypted token string.
        key: A URL-safe base64-encoded 32-byte key.

    Returns the original plaintext string.
    """
    fernet = Fernet(key.encode())
    return fernet.decrypt(token.encode()).decode()
