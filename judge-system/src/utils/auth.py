"""
Authentication and Authorization components
認証・認可システム
"""

import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from enum import Enum
import logging
from dataclasses import dataclass

from ..env import settings
from ..const import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_MINUTES
from .logging import get_logger

logger = get_logger(__name__)


class Role(str, Enum):
    """ユーザーロール"""

    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    GUEST = "guest"


class Permission(str, Enum):
    """権限"""

    # 問題管理
    PROBLEM_CREATE = "problem:create"
    PROBLEM_READ = "problem:read"
    PROBLEM_UPDATE = "problem:update"
    PROBLEM_DELETE = "problem:delete"

    # テストケース管理
    JUDGECASE_CREATE = "judgecase:create"
    JUDGECASE_READ = "judgecase:read"
    JUDGECASE_UPDATE = "judgecase:update"
    JUDGECASE_DELETE = "judgecase:delete"

    # 提出管理
    SUBMISSION_CREATE = "submission:create"
    SUBMISSION_READ = "submission:read"
    SUBMISSION_READ_ALL = "submission:read_all"
    SUBMISSION_DELETE = "submission:delete"

    # ジャッジ管理
    JUDGE_EXECUTE = "judge:execute"
    JUDGE_READ = "judge:read"
    JUDGE_READ_ALL = "judge:read_all"
    JUDGE_MANAGE = "judge:manage"

    # ユーザー管理
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_MANAGE_ROLES = "user:manage_roles"

    # システム管理
    SYSTEM_ADMIN = "system:admin"
    SYSTEM_MONITOR = "system:monitor"


# ロールと権限のマッピング
ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permission.PROBLEM_CREATE,
        Permission.PROBLEM_READ,
        Permission.PROBLEM_UPDATE,
        Permission.PROBLEM_DELETE,
        Permission.JUDGECASE_CREATE,
        Permission.JUDGECASE_READ,
        Permission.JUDGECASE_UPDATE,
        Permission.JUDGECASE_DELETE,
        Permission.SUBMISSION_CREATE,
        Permission.SUBMISSION_READ,
        Permission.SUBMISSION_READ_ALL,
        Permission.SUBMISSION_DELETE,
        Permission.JUDGE_EXECUTE,
        Permission.JUDGE_READ,
        Permission.JUDGE_READ_ALL,
        Permission.JUDGE_MANAGE,
        Permission.USER_CREATE,
        Permission.USER_READ,
        Permission.USER_UPDATE,
        Permission.USER_DELETE,
        Permission.USER_MANAGE_ROLES,
        Permission.SYSTEM_ADMIN,
        Permission.SYSTEM_MONITOR,
    ],
    Role.MODERATOR: [
        Permission.PROBLEM_READ,
        Permission.PROBLEM_UPDATE,
        Permission.JUDGECASE_READ,
        Permission.JUDGECASE_UPDATE,
        Permission.SUBMISSION_READ,
        Permission.SUBMISSION_READ_ALL,
        Permission.JUDGE_READ,
        Permission.JUDGE_READ_ALL,
        Permission.USER_READ,
        Permission.SYSTEM_MONITOR,
    ],
    Role.USER: [
        Permission.PROBLEM_READ,
        Permission.JUDGECASE_READ,
        Permission.SUBMISSION_CREATE,
        Permission.SUBMISSION_READ,
        Permission.JUDGE_EXECUTE,
        Permission.JUDGE_READ,
    ],
    Role.GUEST: [
        Permission.PROBLEM_READ,
        Permission.JUDGECASE_READ,
    ],
}


@dataclass
class UserClaims:
    """JWTクレーム"""

    user_id: str
    email: str
    username: str
    roles: List[Role]
    permissions: List[Permission]
    exp: datetime
    iat: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "username": self.username,
            "roles": [role.value for role in self.roles],
            "permissions": [perm.value for perm in self.permissions],
            "exp": int(self.exp.timestamp()),
            "iat": int(self.iat.timestamp()),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserClaims":
        return cls(
            user_id=data["user_id"],
            email=data["email"],
            username=data["username"],
            roles=[Role(r) for r in data["roles"]],
            permissions=[Permission(p) for p in data["permissions"]],
            exp=datetime.fromtimestamp(data["exp"]),
            iat=datetime.fromtimestamp(data["iat"]),
        )


class PasswordManager:
    """パスワード管理"""

    @staticmethod
    def hash_password(password: str) -> str:
        """パスワードをハッシュ化"""
        salt = secrets.token_hex(32)
        pwdhash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
        )
        return salt + pwdhash.hex()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """パスワードを検証"""
        salt = hashed[:64]
        stored_hash = hashed[64:]
        pwdhash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
        )
        return pwdhash.hex() == stored_hash


class JWTManager:
    """JWT管理"""

    def __init__(
        self, secret_key: str = JWT_SECRET_KEY, algorithm: str = JWT_ALGORITHM
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def create_token(self, user_claims: UserClaims) -> str:
        """JWTトークンを作成"""
        try:
            payload = user_claims.to_dict()
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.debug(f"JWT token created for user: {user_claims.user_id}")
            return token
        except Exception as e:
            logger.error(f"Failed to create JWT token: {e}")
            raise

    def verify_token(self, token: str) -> Optional[UserClaims]:
        """JWTトークンを検証"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            claims = UserClaims.from_dict(payload)

            # 有効期限チェック
            if datetime.now() > claims.exp:
                logger.warning(f"Expired token for user: {claims.user_id}")
                return None

            return claims
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None

    def refresh_token(self, token: str) -> Optional[str]:
        """トークンをリフレッシュ"""
        claims = self.verify_token(token)
        if not claims:
            return None

        # 新しい有効期限でトークンを再作成
        new_claims = UserClaims(
            user_id=claims.user_id,
            email=claims.email,
            username=claims.username,
            roles=claims.roles,
            permissions=claims.permissions,
            exp=datetime.now() + timedelta(minutes=JWT_EXPIRE_MINUTES),
            iat=datetime.now(),
        )

        return self.create_token(new_claims)


class AuthenticationService:
    """認証サービス"""

    def __init__(self, jwt_manager: JWTManager):
        self.jwt_manager = jwt_manager
        self.password_manager = PasswordManager()

    def create_user_claims(
        self, user_id: str, email: str, username: str, roles: List[Role]
    ) -> UserClaims:
        """ユーザークレームを作成"""
        # ロールから権限を集約
        permissions = set()
        for role in roles:
            permissions.update(ROLE_PERMISSIONS.get(role, []))

        return UserClaims(
            user_id=user_id,
            email=email,
            username=username,
            roles=roles,
            permissions=list(permissions),
            exp=datetime.now() + timedelta(minutes=JWT_EXPIRE_MINUTES),
            iat=datetime.now(),
        )

    def authenticate_user(
        self, email: str, password: str, stored_hash: str, roles: List[Role]
    ) -> Optional[str]:
        """ユーザーを認証してトークンを返す"""
        if not self.password_manager.verify_password(password, stored_hash):
            logger.warning(f"Authentication failed for email: {email}")
            return None

        # ユーザー情報からクレームを作成（実際の実装では DB から取得）
        claims = self.create_user_claims(
            user_id="user_id_from_db",  # 実際は DB から取得
            email=email,
            username="username_from_db",  # 実際は DB から取得
            roles=roles,
        )

        token = self.jwt_manager.create_token(claims)
        logger.info(f"User authenticated successfully: {email}")
        return token

    def register_user(
        self,
        email: str,
        username: str,
        password: str,
        roles: Optional[List[Role]] = None,
    ) -> Dict[str, Any]:
        """ユーザーを登録"""
        if roles is None:
            roles = [Role.USER]

        hashed_password = self.password_manager.hash_password(password)

        # 実際の実装では DB にユーザーを保存
        user_id = f"user_{secrets.token_hex(8)}"

        claims = self.create_user_claims(user_id, email, username, roles)
        token = self.jwt_manager.create_token(claims)

        logger.info(f"User registered successfully: {email}")

        return {
            "user_id": user_id,
            "email": email,
            "username": username,
            "token": token,
            "hashed_password": hashed_password,
        }


class AuthorizationService:
    """認可サービス"""

    def __init__(self):
        pass

    def check_permission(
        self, user_claims: UserClaims, required_permission: Permission
    ) -> bool:
        """権限をチェック"""
        return required_permission in user_claims.permissions

    def check_role(self, user_claims: UserClaims, required_role: Role) -> bool:
        """ロールをチェック"""
        return required_role in user_claims.roles

    def check_resource_access(
        self,
        user_claims: UserClaims,
        resource_owner_id: str,
        required_permission: Permission,
    ) -> bool:
        """リソースアクセス権をチェック"""
        # 管理者は全てアクセス可能
        if Role.ADMIN in user_claims.roles:
            return True

        # リソースの所有者は基本的にアクセス可能
        if user_claims.user_id == resource_owner_id:
            # 読み取り権限があるかチェック
            read_permissions = [
                Permission.SUBMISSION_READ,
                Permission.JUDGE_READ,
                Permission.USER_READ,
            ]
            return any(perm in user_claims.permissions for perm in read_permissions)

        # その他は明示的な権限が必要
        return required_permission in user_claims.permissions


# セキュリティデコレータ
def require_authentication(func):
    """認証が必要な関数に付けるデコレータ"""

    async def wrapper(*args, **kwargs):
        # 実際の実装では request から token を取得
        token = kwargs.get("token")
        if not token:
            raise PermissionError("Authentication required")

        jwt_manager = JWTManager()
        user_claims = jwt_manager.verify_token(token)
        if not user_claims:
            raise PermissionError("Invalid or expired token")

        kwargs["user_claims"] = user_claims
        return await func(*args, **kwargs)

    return wrapper


def require_permission(permission: Permission):
    """特定の権限が必要な関数に付けるデコレータ"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            user_claims = kwargs.get("user_claims")
            if not user_claims:
                raise PermissionError("User claims not found")

            auth_service = AuthorizationService()
            if not auth_service.check_permission(user_claims, permission):
                raise PermissionError(f"Permission required: {permission.value}")

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_role(role: Role):
    """特定のロールが必要な関数に付けるデコレータ"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            user_claims = kwargs.get("user_claims")
            if not user_claims:
                raise PermissionError("User claims not found")

            auth_service = AuthorizationService()
            if not auth_service.check_role(user_claims, role):
                raise PermissionError(f"Role required: {role.value}")

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# FastAPI Dependencies
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


@dataclass
class User:
    """認証済みユーザー情報"""

    user_id: str
    email: str
    username: str
    roles: List[Role]
    permissions: List[Permission]

    def has_permission(self, permission: Permission) -> bool:
        """権限を持っているかチェック"""
        return permission in self.permissions

    def has_role(self, role: Role) -> bool:
        """ロールを持っているかチェック"""
        return role in self.roles

    def is_admin(self) -> bool:
        """管理者かどうか"""
        return Role.ADMIN in self.roles

    def is_moderator(self) -> bool:
        """モデレーター以上かどうか"""
        return Role.ADMIN in self.roles or Role.MODERATOR in self.roles

    def can_access_resource(self, resource_owner_id: str) -> bool:
        """リソースにアクセスできるかチェック"""
        # 管理者は全てアクセス可能
        if self.is_admin():
            return True

        # 自分のリソースならアクセス可能
        if self.user_id == resource_owner_id:
            return True

        # モデレーターは他人のリソースも見れる
        if self.is_moderator():
            return True

        return False


# FastAPI Security
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """現在のユーザーを取得（FastAPI Dependency）"""
    token = credentials.credentials

    # トークンを検証
    claims = jwt_manager.verify_token(token)
    if not claims:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return User(
        user_id=claims.user_id,
        email=claims.email,
        username=claims.username,
        roles=claims.roles,
        permissions=claims.permissions,
    )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[User]:
    """オプショナルユーザー（未認証でもOK）"""
    if not credentials:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """管理者権限が必要"""
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


async def require_moderator(current_user: User = Depends(get_current_user)) -> User:
    """モデレーター以上の権限が必要"""
    if not current_user.is_moderator():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Moderator access required",
        )
    return current_user


def require_permission_dependency(permission: Permission):
    """特定の権限が必要なDependency"""

    async def check_permission(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission.value}",
            )
        return current_user

    return check_permission


# 便利関数
def create_access_token(
    user_id: str, email: str, username: str, roles: List[Role]
) -> str:
    """アクセストークンを作成"""
    claims = auth_service.create_user_claims(user_id, email, username, roles)
    return jwt_manager.create_token(claims)


def verify_access_token(token: str) -> Optional[UserClaims]:
    """アクセストークンを検証"""
    return jwt_manager.verify_token(token)


# グローバルインスタンス
jwt_manager = JWTManager()
auth_service = AuthenticationService(jwt_manager)
authz_service = AuthorizationService()
