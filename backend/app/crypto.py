from cryptography.fernet import Fernet
import os

KEY_ENV = "SMARTCLIP_MASTER_KEY"

def _get_fernet_or_none():
    key = os.getenv(KEY_ENV)
    if not key:
        return None
    try:
        return Fernet(key)
    except Exception:
        # invalid key
        return None

def encrypt(plaintext: str) -> str:
    if plaintext is None:
        return None
    f = _get_fernet_or_none()
    if not f:
        # No key configured; return plaintext (warning: not encrypted)
        return plaintext
    return f.encrypt(plaintext.encode('utf-8')).decode('utf-8')

def decrypt(token: str) -> str:
    if token is None:
        return None
    f = _get_fernet_or_none()
    if not f:
        # No key configured; assume token is plaintext
        return token
    return f.decrypt(token.encode('utf-8')).decode('utf-8')
