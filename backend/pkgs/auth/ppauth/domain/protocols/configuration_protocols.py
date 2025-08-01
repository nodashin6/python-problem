"""
Configuration Protocols for Auth Domain
認証ドメイン設定プロトコル - インフラストラクチャに依存しない設定抽象化
"""

from abc import ABC, abstractmethod
from typing import Optional

# Use Pydantic directly to avoid cross-module dependency
from pydantic import BaseModel, ConfigDict


class DatabaseConfig(BaseModel):
    """データベース接続設定"""
    
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)
    
    url: str
    key: str
    timeout: Optional[float] = None
    max_connections: Optional[int] = None


class JWTConfig(BaseModel):
    """JWT設定"""
    
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)
    
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7


class PasswordConfig(BaseModel):
    """パスワードハッシュ設定"""
    
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)
    
    salt_length: int = 32
    iterations: int = 100000
    hash_length: int = 64


class AuthConfig(BaseModel):
    """認証システム全体の設定"""
    
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)
    
    database: DatabaseConfig
    jwt: JWTConfig
    password: PasswordConfig
    
    # Optional features
    enable_refresh_tokens: bool = True
    enable_email_verification: bool = False
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15


class ConfigurationProvider(ABC):
    """設定プロバイダ抽象化"""
    
    @abstractmethod
    def get_auth_config(self) -> AuthConfig:
        """認証設定を取得"""
        pass
    
    @abstractmethod
    def get_database_config(self) -> DatabaseConfig:
        """データベース設定を取得"""
        pass
    
    @abstractmethod
    def get_jwt_config(self) -> JWTConfig:
        """JWT設定を取得"""
        pass
    
    @abstractmethod
    def get_password_config(self) -> PasswordConfig:
        """パスワード設定を取得"""
        pass