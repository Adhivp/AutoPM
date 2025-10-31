"""
Password hashing utilities using SHA256
"""
import hashlib


def hash_password(password: str) -> str:
    """
    Hash a password using SHA256
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password string (SHA256 hex digest)
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
    
    Returns:
        True if password matches, False otherwise
    """
    return hash_password(plain_password) == hashed_password
