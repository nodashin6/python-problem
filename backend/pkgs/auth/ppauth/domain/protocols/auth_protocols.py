"""
Authentication Protocols for Domain Layer
認証ドメインレイヤー用プロトコル - インフラストラクチャに依存しない抽象化
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from ..models.user import User
from ..value_objects.jwt_token import JWTClaims, JWTToken


class CryptoProvider(ABC):
    """
    Cryptographic Provider Protocol
    暗号化プロバイダープロトコル - 具体的な暗号化実装はインフラ層
    """

    @abstractmethod
    def pbkdf2_hash(self, password: str, salt: str, iterations: int) -> str:
        """PBKDF2 hash with salt"""
        pass

    @abstractmethod
    def generate_salt(self, length: int = 32) -> str:
        """Generate random salt"""
        pass


class JWTEncoder(ABC):
    """
    JWT Encoding Protocol
    JWTエンコーディングプロトコル - 具体的な実装はインフラ層
    """

    @abstractmethod
    def encode_claims(self, claims: JWTClaims) -> str:
        """Encode claims to JWT string"""
        pass

    @abstractmethod
    def decode_token(self, token: str) -> Optional[JWTClaims]:
        """Decode JWT string to claims"""
        pass


class TokenManager(ABC):
    """
    Token Management Protocol
    トークン管理プロトコル - ドメインロジック
    """

    @abstractmethod
    def create_token_for_user(self, user: User) -> JWTToken:
        """Create JWT token for user"""
        pass

    @abstractmethod
    def verify_token(self, raw_token: str) -> Optional[JWTToken]:
        """Verify and decode raw token string"""
        pass


class AuthenticationError(Exception):
    """Authentication related error"""
    pass


class AuthorizationError(Exception):
    """Authorization related error"""
    pass


class TokenExpiredError(AuthenticationError):
    """Token expired error"""
    pass


class InvalidTokenError(AuthenticationError):
    """Invalid token error"""
    pass


class Logger(ABC):
    """
    Logger Protocol
    ログ出力プロトコル
    """

    @abstractmethod
    def info(self, message: str) -> None:
        """Log info message"""
        pass

    @abstractmethod
    def warning(self, message: str) -> None:
        """Log warning message"""
        pass

    @abstractmethod
    def error(self, message: str) -> None:
        """Log error message"""
        pass