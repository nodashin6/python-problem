"""
Authentication and Authorization components
認証・認可システム
"""

import hashlib
import logging
import secrets
from datetime import datetime, timedelta
from typing import Any

import jwt

from src.const import JWT_ALGORITHM, JWT_EXPIRE_MINUTES, JWT_SECRET_KEY
from src.utils.logging import get_logger

from ...models.user import User


class JWTManager:
    """JWT管理"""

    def __init__(
        self,
        secret_key: str = JWT_SECRET_KEY,
        algorithm: str = JWT_ALGORITHM,
        logger: logging.Logger | None = None,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.logger = logger or get_logger(__name__)

    def create_token(self, user: User, expires_delta: timedelta | None = None) -> str:
        """JWTトークンを作成"""
        try:
            if expires_delta is None:
                expires_delta = timedelta(minutes=JWT_EXPIRE_MINUTES)
            payload = user.to_jwt_claims(expires_delta)
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            self.logger.debug(f"JWT token created for user: {user.id}")
            return token
        except Exception as e:
            self.logger.error(f"Failed to create JWT token: {e}")
            raise

    def verify_token(self, token: str) -> User | None:
        """JWTトークンを検証"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user = User.from_jwt_claims(payload)

            # 有効期限チェック
            if user.exp and datetime.now() > user.exp:
                self.logger.warning(f"Expired token for user: {user.id}")
                return None

            return user
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Token verification error: {e}")
            return None

    def refresh_token(self, token: str) -> str | None:
        """トークンをリフレッシュ"""
        user = self.verify_token(token)
        if not user:
            return None

        # 新しい有効期限でトークンを再作成
        expires_delta = timedelta(minutes=JWT_EXPIRE_MINUTES)
        return self.create_token(user, expires_delta)
