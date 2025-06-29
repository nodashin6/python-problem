"""
Core Common Helpers
コア共通ヘルパー群 - 暗号化機能
"""

import hashlib
import secrets
from typing import Final


class CryptographyHelper:
    """Helper for cryptographic operations"""

    SALT_LENGTH: Final[int] = 32
    HASH_ALGORITHM: Final[str] = "sha256"

    @staticmethod
    def generate_salt() -> str:
        """Generate a random salt"""
        return secrets.token_hex(CryptographyHelper.SALT_LENGTH)

    @staticmethod
    def hash_with_salt(data: str, salt: str) -> str:
        """Hash data with salt"""
        hash_object = hashlib.new(CryptographyHelper.HASH_ALGORITHM)
        hash_object.update((data + salt).encode("utf-8"))
        return hash_object.hexdigest()

    @staticmethod
    def verify_hash(data: str, salt: str, expected_hash: str) -> bool:
        """Verify data against hash"""
        actual_hash = CryptographyHelper.hash_with_salt(data, salt)
        return actual_hash == expected_hash

    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate secure random token"""
        return secrets.token_urlsafe(length)
