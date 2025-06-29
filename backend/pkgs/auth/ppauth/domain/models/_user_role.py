from pydantic import BaseModel, ConfigDict, Field

from ..enums import Permission, UserRole


class Role(BaseModel):
    """ユーザーロールモデル"""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    user_role: UserRole = Field(..., description="ユーザーロールの種類")
    permissions: list[Permission] = Field(
        default_factory=list, description="このロールに関連する権限のリスト"
    )
    description: str | None = Field(None, description="ロールの説明")

    def __str__(self) -> str:
        """ロールの文字列表現"""
        return f"Role(user_role={self.user_role}, permissions={self.permissions}, description={self.description})"
