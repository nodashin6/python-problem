"""
Authentication and Authorization components
認証・認可システム
"""

import hashlib
import logging
import secrets


class PasswordManager:
    """パスワード管理"""

    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger

    @staticmethod
    def hash_password(password: str) -> str:
        """パスワードをハッシュ化"""
        salt = secrets.token_hex(32)
        pwdhash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
        return salt + pwdhash.hex()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """パスワードを検証"""
        salt = hashed[:64]
        stored_hash = hashed[64:]
        pwdhash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
        return pwdhash.hex() == stored_hash
