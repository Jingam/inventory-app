import hashlib
import hmac
import os

VALID_ROLES = ('admin', 'manager', 'technician', 'viewer')


def hash_password(password: str, salt: bytes | None = None) -> str:
    if salt is None:
        salt = os.urandom(16)
    derived = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 200000)
    return f"{salt.hex()}${derived.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        salt_hex, hash_hex = encoded.split('$', 1)
        salt = bytes.fromhex(salt_hex)
    except (ValueError, TypeError):
        return False

    candidate = hash_password(password, salt)
    return hmac.compare_digest(candidate, encoded)


def normalize_role(role: str) -> str:
    if not role:
        return ''
    return role.strip().lower()


def is_valid_role(role: str) -> bool:
    return normalize_role(role) in VALID_ROLES
