from datetime import datetime

from pydantic import UUID4, EmailStr, Field, field_validator
from pydddi import IEntity

from ..enums import UserRole


class UserEntity(IEntity):
    """
    Represents a user entity.
    This class contains fields that represent the user's properties.
    """

    id: UUID4
    email: EmailStr
    user_name: str
    password_hash: str
    display_name: str
    bio: str = Field(default="")
    avatar_url: str = Field(default="")
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    role: UserRole = Field(default=UserRole.USER)
    last_login_at: datetime | None = None
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)

    @field_validator("email")
    def validate_email(cls, value: EmailStr) -> EmailStr:
        if not value:
            raise ValueError("Email cannot be empty")
        return value

    @field_validator("user_name")
    def validate_user_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("user_name cannot be empty")
        if len(value) < 3:
            raise ValueError("user_name must be at least 3 characters long")
        if len(value) > 50:
            raise ValueError("user_name must be at most 50 characters long")
        return value.strip()

    @field_validator("display_name")
    def validate_display_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Display name cannot be empty")
        return value.strip()

    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == UserRole.ADMIN

    def deactivate(self) -> None:
        """Deactivate user account"""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def verify_email(self) -> None:
        """Verify user email"""
        self.is_verified = True
        self.updated_at = datetime.utcnow()

    def update_last_login(self) -> None:
        """Update last login timestamp"""
        self.last_login_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def update_profile(self, display_name: str = None, bio: str = None, avatar_url: str = None) -> None:
        """Update user profile information"""
        if display_name is not None:
            self.display_name = display_name
        if bio is not None:
            self.bio = bio
        if avatar_url is not None:
            self.avatar_url = avatar_url
        self.updated_at = datetime.utcnow()
