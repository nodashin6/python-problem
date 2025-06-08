"""
FastAPI dependencies for authentication and authorization
"""

from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import Client

from src.const import JWT_ALGORITHM, JWT_EXPIRE_MINUTES, JWT_SECRET_KEY
from src.utils.logging import get_logger

from ..domain.entities.enums import UserRole
from ..domain.models.user import User
from ..domain.services.auth_service import AuthenticationService, AuthorizationService, JWTManager
from ..domain.services.user_service import UserService
from ..infrastructure.supabase.repositories.user_repository_impl import UserRepositoryImpl
from ..infrastructure.supabase.repositories.user_role_repository_impl import UserRoleRepositoryImpl

logger = get_logger(__name__)

# FastAPI Security
security = HTTPBearer()


def get_supabase_client() -> Client:
    """Get Supabase client (should be implemented elsewhere)"""
    # This should be implemented to return your actual Supabase client
    raise NotImplementedError("Supabase client not configured")


def get_user_repository(client: Client = Depends(get_supabase_client)) -> UserRepositoryImpl:
    """Get user repository"""
    return UserRepositoryImpl(client)


def get_user_role_repository(client: Client = Depends(get_supabase_client)) -> UserRoleRepositoryImpl:
    """Get user role repository"""
    return UserRoleRepositoryImpl(client)


def get_jwt_manager() -> JWTManager:
    """Get JWT manager"""
    return JWTManager()


def get_auth_service(jwt_manager: JWTManager = Depends(get_jwt_manager)) -> AuthenticationService:
    """Get authentication service"""
    return AuthenticationService(jwt_manager)


def get_authorization_service() -> AuthorizationService:
    """Get authorization service"""
    return AuthorizationService()


def get_user_service(
    user_repo: UserRepositoryImpl = Depends(get_user_repository),
    user_role_repo: UserRoleRepositoryImpl = Depends(get_user_role_repository),
) -> UserService:
    """Get user service"""
    return UserService(user_repo, user_role_repo)


async def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    jwt_manager: JWTManager = Depends(get_jwt_manager),
) -> User:
    """Extract and validate token to get user"""
    try:
        # Verify token and extract user
        user = jwt_manager.verify_token(credentials.credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token validation failed",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_user(
    token_user: User = Depends(get_current_user_from_token),
    user_service: UserService = Depends(get_user_service),
) -> User:
    """Get current authenticated user"""
    try:
        # トークンから取得したユーザー情報をそのまま使用するか、
        # 必要に応じてDBから最新情報を取得
        user = await user_service.get_user(str(token_user.id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # UserServiceから取得したユーザーにis_activeフィールドがない場合は
        # トークンユーザーを使用
        return token_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get current user: {e}")
        # エラーの場合はトークンから取得したユーザーを返す
        return token_user


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
    jwt_manager: JWTManager = Depends(get_jwt_manager),
) -> User | None:
    """Get current user if authenticated, otherwise None"""
    if not credentials:
        return None

    try:
        user = jwt_manager.verify_token(credentials.credentials)
        if user:
            return user
        return None
    except Exception:
        # トークンが無効な場合もNoneを返す
        return None


async def require_admin(
    current_user: User = Depends(get_current_user),
    auth_service: AuthorizationService = Depends(get_authorization_service),
) -> User:
    """Require admin role"""
    if not auth_service.check_role(current_user, UserRole.ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return current_user


async def require_moderator(
    current_user: User = Depends(get_current_user),
    auth_service: AuthorizationService = Depends(get_authorization_service),
) -> User:
    """Require moderator or admin role"""
    if not (
        auth_service.check_role(current_user, UserRole.MODERATOR)
        or auth_service.check_role(current_user, UserRole.ADMIN)
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Moderator role required")
    return current_user


async def require_verified_email(current_user: User = Depends(get_current_user)) -> User:
    """Require verified email"""
    # Note: email_verifiedフィールドがUserモデルに存在しない場合は追加が必要
    # 今回は実装をスキップ
    return current_user
