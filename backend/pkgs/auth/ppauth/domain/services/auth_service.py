"""
Authentication and Authorization components
認証・認可システム
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydddi import IDomainService

from src.const import JWT_ALGORITHM, JWT_EXPIRE_MINUTES, JWT_SECRET_KEY
from src.utils.logging import get_logger

from ..entities.enums import ROLE_PERMISSIONS, Permission, UserRole
from ..models.user import User

logger = get_logger(__name__)


class PasswordManager:
    """パスワード管理"""

    @staticmethod
    def hash_password(password: str) -> str:
        """パスワードをハッシュ化"""
        salt = secrets.token_hex(32)
        pwdhash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
        return salt + pwdhash.hex()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """パスワードを検証"""
        salt = hashed[:64]
        stored_hash = hashed[64:]
        pwdhash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
        return pwdhash.hex() == stored_hash


class JWTManager:
    """JWT管理"""

    def __init__(self, secret_key: str = JWT_SECRET_KEY, algorithm: str = JWT_ALGORITHM):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def create_token(self, user: User, expires_delta: timedelta | None = None) -> str:
        """JWTトークンを作成"""
        try:
            if expires_delta is None:
                expires_delta = timedelta(minutes=JWT_EXPIRE_MINUTES)
            payload = user.to_jwt_claims(expires_delta)
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.debug(f"JWT token created for user: {user.id}")
            return token
        except Exception as e:
            logger.error(f"Failed to create JWT token: {e}")
            raise

    def verify_token(self, token: str) -> User | None:
        """JWTトークンを検証"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user = User.from_jwt_claims(payload)

            # 有効期限チェック
            if user.exp and datetime.now() > user.exp:
                logger.warning(f"Expired token for user: {user.id}")
                return None

            return user
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None

    def refresh_token(self, token: str) -> str | None:
        """トークンをリフレッシュ"""
        user = self.verify_token(token)
        if not user:
            return None

        # 新しい有効期限でトークンを再作成
        expires_delta = timedelta(minutes=JWT_EXPIRE_MINUTES)
        return self.create_token(user, expires_delta)


class AuthenticationService(IDomainService):
    """認証サービス"""

    def __init__(self, jwt_manager: JWTManager):
        self.jwt_manager = jwt_manager
        self.password_manager = PasswordManager()

    def create_user(
        self, user_id: str, email: str, username: str, display_name: str, role: UserRole
    ) -> User:
        """ユーザーを作成"""
        # ロールから権限を取得
        permissions = ROLE_PERMISSIONS.get(role, [])

        return User(
            id=user_id,
            email=email,
            username=username,
            display_name=display_name,
            role=role,
            permissions=permissions,
        )

    async def authenticate_user(self, email: str, password: str) -> User | None:
        """ユーザーを認証してUserオブジェクトを返す"""
        # 実際の実装では UserService や UserRepository を使用してDBから取得
        # 今回は簡略化

        # ユーザーをメールで検索 (実装例)
        # user_entity = await self.user_service.get_user_by_email(email)
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
            logger.warning(f"Authentication failed for email: {email}")
            return None

        # ユーザー情報を作成 (実際の実装では DB から取得)
        user = self.create_user(
            user_id="user_id_from_db",  # 実際は DB から取得
            email=email,
            username="username_from_db",  # 実際は DB から取得
            display_name="display_name_from_db",  # 実際は DB から取得
            role=role,
        )

        logger.info(f"User authenticated successfully: {email}")
        return user

    def create_access_token(self, user: User) -> str:
        """アクセストークンを作成"""
        return self.jwt_manager.create_token(user)

    def register_user(
        self,
        email: str,
        username: str,
        password: str,
        role: UserRole | None = None,
    ) -> dict[str, Any]:
        """ユーザーを登録"""
        if role is None:
            role = UserRole.USER

        hashed_password = self.password_manager.hash_password(password)

        # 実際の実装では DB にユーザーを保存
        user_id = f"user_{secrets.token_hex(8)}"

        user = self.create_user(user_id, email, username, username, role)  # display_nameはusernameと同じ
        token = self.jwt_manager.create_token(user)

        logger.info(f"User registered successfully: {email}")

        return {
            "user_id": user_id,
            "email": email,
            "username": username,
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

        jwt_manager = JWTManager()
        user = jwt_manager.verify_token(token)
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


# グローバルインスタンス
jwt_manager = JWTManager()
auth_service = AuthenticationService(jwt_manager)
authz_service = AuthorizationService()
