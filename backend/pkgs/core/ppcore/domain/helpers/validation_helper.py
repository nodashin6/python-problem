"""
Validation Helper
検証ヘルパー
"""

import re
from typing import Final

# Constants
EMAIL_PATTERN: Final[str] = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
user_name_PATTERN: Final[str] = r"^[a-zA-Z0-9_]{3,30}$"


class ValidationHelper:
    """Helper for validation operations"""

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email format"""
        return bool(re.match(EMAIL_PATTERN, email))

    @staticmethod
    def is_valid_user_name(user_name: str) -> bool:
        """Validate user_name format"""
        return bool(re.match(user_name_PATTERN, user_name))

    @staticmethod
    def is_valid_password(password: str) -> bool:
        """Validate password strength"""
        return len(password) >= 8

    @staticmethod
    def validate_user_input(user_name: str, email: str, password: str) -> list[str]:
        """Validate user registration input"""
        errors = []

        if not ValidationHelper.is_valid_user_name(user_name):
            errors.append(
                "user_name must be 3-30 characters long and contain only letters, numbers, and underscores"
            )

        if not ValidationHelper.is_valid_email(email):
            errors.append("Invalid email format")

        if not ValidationHelper.is_valid_password(password):
            errors.append("Password must be at least 8 characters long")

        return errors
