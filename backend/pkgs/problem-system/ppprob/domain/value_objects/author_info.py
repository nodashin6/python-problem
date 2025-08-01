"""
Author Value Object for Problem Domain
問題ドメインの著者バリューオブジェクト - 外部依存を排除
"""

from pydantic import UUID4, BaseModel, ConfigDict, Field


class AuthorInfo(BaseModel):
    """
    Author information value object
    著者情報のバリューオブジェクト
    
    This replaces direct dependency on ppauth.UserEntity
    これは ppauth.UserEntity への直接依存を置き換える
    """
    
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)
    
    id: UUID4 = Field(..., description="Author user ID")
    user_name: str = Field(..., description="Author username")
    display_name: str = Field(..., description="Author display name")  
    email: str = Field(..., description="Author email")
    avatar_url: str | None = Field(None, description="Author avatar URL")
    
    @classmethod
    def from_user_data(cls, user_data: dict) -> "AuthorInfo":
        """Create AuthorInfo from user data dictionary"""
        return cls(
            id=user_data["id"],
            user_name=user_data["user_name"],
            display_name=user_data["display_name"],
            email=user_data["email"],
            avatar_url=user_data.get("avatar_url")
        )