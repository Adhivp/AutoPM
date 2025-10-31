"""
Encryption utilities for storing sensitive tokens
"""
from cryptography.fernet import Fernet
from config import settings


def get_cipher():
    """Get Fernet cipher instance using the encryption key from settings"""
    return Fernet(settings.ENCRYPTION_KEY.encode())


def encrypt_token(token: str) -> str:
    """
    Encrypt a token using Fernet symmetric encryption
    
    Args:
        token: Plain text token to encrypt
    
    Returns:
        Encrypted token as string
    """
    cipher = get_cipher()
    return cipher.encrypt(token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    """
    Decrypt a token using Fernet symmetric encryption
    
    Args:
        encrypted_token: Encrypted token string
    
    Returns:
        Decrypted plain text token
    """
    cipher = get_cipher()
    return cipher.decrypt(encrypted_token.encode()).decode()
