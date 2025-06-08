"""
User model for authentication
認証用ユーザーモデル
"""

from datetime import datetime, timedelta
from typing import Any

from pydantic import UUID4
from pydddi import IModel

from ..entities.enums import Permission, UserRole


class User(IModel):
    """認証済みユーザー情報 - JWTクレームも兼ねる"""

    id: UUID4
    email: str
    username: str
    display_name: str
    role: UserRole  # 単一ロールに変更
    permissions: list[Permission]
    # ユーザープロフィール関連
    avatar_url: str | None = None
    bio: str | None = None
    is_active: bool = True
    created_at: datetime | None = None
    # JWT関連フィールド（オプション）
    exp: datetime | None = None
    iat: datetime | None = None

    def has_permission(self, permission: Permission) -> bool:
        """権限を持っているかチェック"""
        return permission in self.permissions

    def has_role(self, role: UserRole) -> bool:
        """ロールを持っているかチェック"""
        return self.role == role

    def is_admin(self) -> bool:
        """管理者かどうか"""
        return self.role == UserRole.ADMIN

    def is_moderator(self) -> bool:
        """モデレーター以上かどうか"""
        return self.role in [UserRole.ADMIN, UserRole.MODERATOR]

    def can_access_resource(self, resource_owner_id: str) -> bool:
        """リソースにアクセスできるかチェック"""
        # 管理者は全てアクセス可能
        if self.is_admin():
            return True

        # 自分のリソースならアクセス可能
        if str(self.id) == resource_owner_id:
            return True

        # モデレーターは他人のリソースも見れる
        return self.is_moderator()

    def to_jwt_claims(self, expires_delta: timedelta | None = None) -> dict[str, Any]:
        """JWTクレーム用の辞書に変換"""
        now = datetime.now()
        exp_time = now + (expires_delta or timedelta(minutes=30))

        return {
            "user_id": str(self.id),
            "email": self.email,
            "username": self.username,
            "role": self.role.value,
            "permissions": [perm.value for perm in self.permissions],
            "exp": int(exp_time.timestamp()),
            "iat": int(now.timestamp()),
        }

    @classmethod
    def from_jwt_claims(cls, data: dict[str, Any]) -> "User":
        """JWTクレームから復元"""
        from ..entities.enums import Permission, UserRole

        return cls(
            id=data["user_id"],
            email=data["email"],
            username=data["username"],
            display_name=data.get("display_name", data["username"]),  # fallback
            role=UserRole(data["role"]),
            permissions=[Permission(p) for p in data["permissions"]],
            exp=datetime.fromtimestamp(data["exp"]) if data.get("exp") else None,
            iat=datetime.fromtimestamp(data["iat"]) if data.get("iat") else None,
        )
