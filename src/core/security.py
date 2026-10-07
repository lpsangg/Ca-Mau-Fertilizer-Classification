"""
Security module for password hashing and authentication checks.
Uses SHA-256 with cryptographically secure random salt.
"""

import hashlib
import os

def generate_salt(length: int = 16) -> str:
    """Generate a random hexadecimal salt string."""
    return os.urandom(length).hex()

def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """
    Hash a plaintext password with a salt.
    Returns: (password_hash, salt)
    """
    if salt is None:
        salt = generate_salt()
    salted = f"{password}{salt}".encode("utf-8")
    pwd_hash = hashlib.sha256(salted).hexdigest()
    return pwd_hash, salt

def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Verify if the input password matches the stored hash."""
    test_hash, _ = hash_password(password, salt)
    return test_hash == stored_hash
