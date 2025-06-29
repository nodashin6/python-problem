"""
JWT Token Helper for Auth Domain
認証ドメイン用JWTトークンヘルパー
"""

from datetime import datetime, timedelta
from typing import Any

import jwt


class JWTManager:
    """Helper for JWT token operations in auth domain"""

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def generate_token(self, payload: dict[str, Any], expires_delta: timedelta | None = None) -> str:
        """Generate JWT token"""
        if expires_delta is None:
            expires_delta = timedelta(hours=24)

        expire = datetime.utcnow() + expires_delta
        payload.update({"exp": expire})

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> dict[str, Any] | None:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def extract_user_id(self, token: str) -> str | None:
        """Extract user ID from token"""
        payload = self.verify_token(token)
        if payload:
            return payload.get("user_id")
        return None
