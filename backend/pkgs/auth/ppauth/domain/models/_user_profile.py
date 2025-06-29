from pydantic import BaseModel, Field


class Profile(BaseModel):
    """ユーザープロフィール情報"""

    avatar_url: str | None = Field(None, description="アバター画像のURL")
    bio: str | None = Field(None, description="自己紹介文")
    is_active: bool = Field(True, description="アクティブなユーザーかどうか")
    created_at: str | None = Field(None, description="プロフィール作成日時")
