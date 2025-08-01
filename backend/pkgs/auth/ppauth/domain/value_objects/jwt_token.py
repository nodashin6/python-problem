"""
JWT Token Value Object
JWTトークンバリューオブジェクト - ドメインロジックとしてのJWT
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from pydantic import Field

# Remove cross-module dependency - use Pydantic directly
from pydantic import BaseModel, ConfigDict


class BaseValueObject(BaseModel):
    """Base value object class"""
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)


class JWTClaims(BaseValueObject):
    """
    JWT Claims Value Object
    JWTクレームバリューオブジェクト
    """
    
    user_id: str = Field(...)
    email: str = Field(...)
    user_name: str = Field(...)
    display_name: str = Field(...)
    role: str = Field(...)
    iat: datetime = Field(...)  # issued at
    exp: datetime = Field(...)  # expires at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for token payload"""
        return {
            "user_id": self.user_id,
            "email": self.email,
            "user_name": self.user_name,
            "display_name": self.display_name,
            "role": self.role,
            "iat": int(self.iat.timestamp()),
            "exp": int(self.exp.timestamp()),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JWTClaims":
        """Create from dictionary"""
        return cls(
            user_id=data["user_id"],
            email=data["email"],
            user_name=data["user_name"],
            display_name=data["display_name"],
            role=data["role"],
            iat=datetime.fromtimestamp(data["iat"]),
            exp=datetime.fromtimestamp(data["exp"]),
        )
    
    def is_expired(self) -> bool:
        """Check if token is expired"""
        return datetime.now() > self.exp


class JWTToken(BaseValueObject):
    """
    JWT Token Value Object
    JWTトークンバリューオブジェクト
    """
    
    raw_token: str = Field(...)
    claims: JWTClaims = Field(...)
    
    def is_valid(self) -> bool:
        """Check if token is valid (not expired)"""
        return not self.claims.is_expired()
    
    def get_user_id(self) -> str:
        """Get user ID from token"""
        return self.claims.user_id
    
    def get_user_email(self) -> str:
        """Get user email from token"""
        return self.claims.email
    
    def get_user_role(self) -> str:
        """Get user role from token"""
        return self.claims.role