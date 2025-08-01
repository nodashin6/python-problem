"""
Authentication and Authorization components
認証・認可システム
"""

import secrets
from datetime import datetime, timedelta
from typing import Any, Optional

from pydddi import IDomainService

from ...enums import ROLE_PERMISSIONS, Permission, UserRole
from ...models.user import User
from ...protocols import Logger
from .password_helper import PasswordManager
from .token_helper import JWTManager


class Authentificator(IDomainService):
    """認証サービス"""

    def __init__(
        self,
        jwt_manager: JWTManager,
        password_manager: PasswordManager,
        logger: Logger,
    ):
        self.jwt_manager = jwt_manager
        self.password_manager = password_manager
        self.logger = logger

    def create_user(
        self, user_id: str, email: str, user_name: str, display_name: str, role: UserRole
    ) -> User:
        """ユーザーを作成"""
        # ロールから権限を取得
        permissions = ROLE_PERMISSIONS.get(role, [])

        return User(
            id=user_id,
            email=email,
            user_name=user_name,
            display_name=display_name,
            role=role,
            permissions=permissions,
        )

    async def authenticate_user(self, email: str, password: str) -> User | None:
        """ユーザーを認証してUserオブジェクトを返す"""
        # 実際の実装では UserService や UserRepository を使用してDBから取得
        # 今回は簡略化

        # ユーザーをメールで検索 (実装例)
        # user_entity = await self.user_service.read_user_by_email(email)
        # if not user_entity or not user_entity.is_active:
        #     return None

        # stored_hash = user_entity.password_hash
        # if not self.password_manager.verify_password(password, stored_hash):
        #     logger.warning(f"Authentication failed for email: {email}")
        #     return None

        # 仮実装: 実際にはDBから取得した情報を使用
        stored_hash = "dummy_hash"  # 実装時はDBから取得
        role = UserRole.USER  # 実装時はDBから取得

        if not self.password_manager.verify_password(password, stored_hash):
            self.logger.warning(f"Authentication failed for email: {email}")
            return None

        # ユーザー情報を作成 (実際の実装では DB から取得)
        user = self.create_user(
            user_id="user_id_from_db",  # 実際は DB から取得
            email=email,
            user_name="user_name_from_db",  # 実際は DB から取得
            display_name="display_name_from_db",  # 実際は DB から取得
            role=role,
        )

        self.logger.info(f"User authenticated successfully: {email}")
        return user

    def hash_password(self, password: str) -> str:
        """Hash a password"""
        return self.password_manager.hash_password(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.password_manager.verify_password(password, hashed_password)

    def get_user_from_token(self, token: str) -> User | None:
        """Get user from JWT token"""
        try:
            jwt_token = self.jwt_manager.verify_token(token)
            if not jwt_token:
                return None
                
            payload = jwt_token.claims.to_dict()
            if not payload:
                return None

            user_id = payload.get("user_id")
            email = payload.get("email")

            if not user_id or not email:
                return None

            # 実際の実装では UserService や UserRepository を使用してDBから取得
            # 今回は簡略化してトークンの情報から User を作成
            return User(
                id=user_id,
                email=email,
                user_name=payload.get("user_name", ""),
                display_name=payload.get("display_name", ""),
                role=UserRole(payload.get("role", UserRole.USER.value)),
                permissions=[],  # TODO: 権限を適切に設定
            )

        except Exception as e:
            self.logger.warning(f"Failed to get user from token: {e}")
            return None

    def create_access_token(self, user: User) -> str:
        """アクセストークンを作成"""
        return self.jwt_manager.create_token(user)

    def register_user(
        self,
        email: str,
        user_name: str,
        password: str,
        role: UserRole | None = None,
    ) -> dict[str, Any]:
        """ユーザーを登録"""
        if role is None:
            role = UserRole.USER

        hashed_password = self.password_manager.hash_password(password)

        # 実際の実装では DB にユーザーを保存
        user_id = f"user_{secrets.token_hex(8)}"

        user = self.create_user(user_id, email, user_name, user_name, role)  # display_nameはuser_nameと同じ
        token = self.jwt_manager.create_token(user)

        self.logger.info(f"User registered successfully: {email}")

        return {
            "user_id": user_id,
            "email": email,
            "user_name": user_name,
            "token": token,
            "hashed_password": hashed_password,
        }


class AuthorizationService(IDomainService):
    """認可サービス"""

    def __init__(self):
        pass

    def check_permission(self, user: User, required_permission: Permission) -> bool:
        """権限をチェック"""
        return user.has_permission(required_permission)

    def check_role(self, user: User, required_role: UserRole) -> bool:
        """ロールをチェック"""
        return user.has_role(required_role)

    def check_resource_access(
        self,
        user: User,
        resource_owner_id: str,
    ) -> bool:
        """リソースアクセス権をチェック"""
        return user.can_access_resource(resource_owner_id)


# セキュリティデコレータ
def require_authentication(func):
    """認証が必要な関数に付けるデコレータ"""

    async def wrapper(*args, **kwargs):
        # 実際の実装では request から token を取得
        token = kwargs.get("token")
        if not token:
            raise PermissionError("Authentication required")

        # TODO: Implement with proper dependency injection
        # jwt_manager = get_jwt_manager()
        # jwt_token = jwt_manager.verify_token(token)
        # user = jwt_token.claims if jwt_token else None
        user = None
        if not user:
            raise PermissionError("Invalid or expired token")

        kwargs["user"] = user
        return await func(*args, **kwargs)

    return wrapper


def require_permission(permission: Permission):
    """特定の権限が必要な関数に付けるデコレータ"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            user = kwargs.get("user")
            if not user:
                raise PermissionError("User not found")

            auth_service = AuthorizationService()
            if not auth_service.check_permission(user, permission):
                raise PermissionError(f"Permission required: {permission.value}")

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_role(role: UserRole):
    """特定のロールが必要な関数に付けるデコレータ"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            user = kwargs.get("user")
            if not user:
                raise PermissionError("User not found")

            auth_service = AuthorizationService()
            if not auth_service.check_role(user, role):
                raise PermissionError(f"Role required: {role.value}")

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# グローバルインスタンスは削除 - 依存性注入を使用する
