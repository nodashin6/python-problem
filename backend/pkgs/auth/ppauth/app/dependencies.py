"""
Dependency injection for PPAuth application
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..domain.enums import UserRole
from ..domain.models.user import User
from ..domain.services.auth_service import AuthenticationService
from ..domain.services.user_service import UserService
from ..usecase.create_user_usecase import CreateUserUseCase
from ..usecase.delete_user_usecase import DeleteUserUseCase
from ..usecase.read_user_aggregate_usecase import ReadActiveUsersUseCase
from ..usecase.read_user_by_email_usecase import ReadUserByEmailUseCase
from ..usecase.read_user_by_id_usecase import ReadUserByIdUseCase
from ..usecase.read_users_by_role_usecase import ReadUsersByRoleUseCase
from ..usecase.update_user_usecase import UpdateUserUseCase

security = HTTPBearer()


# Service dependencies
async def get_auth_service() -> AuthenticationService:
    """Get authentication service"""
    # TODO: 実際の実装では DI コンテナから取得


async def get_user_service() -> UserService:
    """Get user service"""
    # TODO: 実際の実装では DI コンテナから取得


# Use case dependencies
async def get_create_user_usecase(
    user_service: UserService = Depends(get_user_service),
) -> CreateUserUseCase:
    """Get create user use case"""
    return CreateUserUseCase(user_service=user_service)


async def get_update_user_usecase(
    user_service: UserService = Depends(get_user_service),
) -> UpdateUserUseCase:
    """Get update user use case"""
    return UpdateUserUseCase(user_service=user_service)


async def get_delete_user_usecase(
    user_service: UserService = Depends(get_user_service),
) -> DeleteUserUseCase:
    """Get delete user use case"""
    return DeleteUserUseCase(user_service=user_service)


async def get_read_user_by_id_usecase(
    user_service: UserService = Depends(get_user_service),
) -> ReadUserByIdUseCase:
    """Get read user by ID use case"""
    return ReadUserByIdUseCase(user_service=user_service)


async def get_read_user_by_email_usecase(
    user_service: UserService = Depends(get_user_service),
) -> ReadUserByEmailUseCase:
    """Get read user by email use case"""
    return ReadUserByEmailUseCase(user_service=user_service)


async def get_read_users_by_role_usecase(
    user_service: UserService = Depends(get_user_service),
) -> ReadUsersByRoleUseCase:
    """Get read users by role use case"""
    return ReadUsersByRoleUseCase(user_service=user_service)


async def get_read_active_users_usecase() -> ReadActiveUsersUseCase:
    """Get read active users use case"""
    # TODO: UserAggregateReadRepository の依存性注入が必要


# Authentication dependencies
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthenticationService = Depends(get_auth_service),
) -> User:
    """Get current authenticated user"""
    try:
        # Token validation and user retrieval
        token = credentials.credentials
        user = await auth_service.get_user_from_token(token)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated",
            )

        return user

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from err


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require admin role"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


async def require_moderator_or_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require moderator or admin role"""
    if current_user.role not in [UserRole.MODERATOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Moderator or admin privileges required",
        )
    return current_user
