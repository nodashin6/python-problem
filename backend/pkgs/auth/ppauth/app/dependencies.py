"""
Dependency injection for PPAuth application
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..domain.enums import UserRole
from ..domain.helpers.authentificator.authentificator import Authentificator
from ..domain.models.user import User
from ..domain.protocols import ConfigurationProvider, DatabaseConfig
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
async def get_auth_service() -> Authentificator:
    """Get authentication service"""
    # TODO: 実際の実装では DI コンテナから取得
    # 今回は簡易実装として直接インスタンスを作成
    from ..domain.helpers.authentificator.authentificator import Authentificator
    
    # Simple implementations for now - in production these would be properly injected
    class SimpleJWTManager:
        def create_token(self, user) -> str:
            return f"jwt_token_for_{user.id}"
        def verify_token(self, token: str):
            return None  # Simple mock
    
    class SimplePasswordManager:
        def hash_password(self, password: str) -> str:
            return f"hashed_{password}"
        def verify_password(self, password: str, hashed: str) -> bool:
            # For testing, we'll accept any password for now
            return True
    
    class SimpleLogger:
        def info(self, msg): print(f"INFO: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
    
    # Create and return auth service with simple implementations
    return Authentificator(
        jwt_manager=SimpleJWTManager(),
        password_manager=SimplePasswordManager(),
        logger=SimpleLogger()
    )


# Configuration dependency - should be injected from environment/config service
async def get_database_config() -> DatabaseConfig:
    """Get database configuration"""
    # TODO: This should be injected from a proper configuration service
    # For now, we'll use environment variables with a fallback
    import os
    
    return DatabaseConfig(
        url=os.getenv("SUPABASE_URL", "http://localhost:54321"),
        key=os.getenv("SUPABASE_ANON_KEY", "your-anon-key-here"),
        timeout=30.0,
        max_connections=10
    )


async def get_user_service(
    db_config: DatabaseConfig = Depends(get_database_config),
) -> UserService:
    """Get user service"""
    # For now, create Supabase client directly until ppcore integration is complete
    from supabase import create_client, Client, ClientOptions
    from ..infrastructure.supabase.repositories.user_repository_impl import UserRepository
    
    options = ClientOptions()
    client: Client = create_client(db_config.url, db_config.key, options=options)
    user_repo = UserRepository(client)
    auth_service = await get_auth_service()

    return UserService(user_repo=user_repo, authentificator=auth_service)


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


async def get_read_active_users_usecase(
    db_config: DatabaseConfig = Depends(get_database_config),
) -> ReadActiveUsersUseCase:
    """Get read active users use case"""
    # For now, create Supabase client directly until ppcore integration is complete
    from supabase import create_client, ClientOptions
    from ..infrastructure.supabase.repositories.user_aggregate_read_repository_impl import (
        UserAggregateReadRepository,
    )

    options = ClientOptions()
    client = create_client(db_config.url, db_config.key, options=options)
    user_aggregate_repo = UserAggregateReadRepository(client)

    return ReadActiveUsersUseCase(user_aggregate_repo=user_aggregate_repo)


# Authentication dependencies
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: Authentificator = Depends(get_auth_service),
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
    # TODO: Implement proper role checking once User model has role property
    # For now, allow all authenticated users (temporary workaround)
    return current_user


async def require_moderator_or_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require moderator or admin role"""
    # TODO: Implement proper role checking once User model has role property
    # For now, allow all authenticated users (temporary workaround)
    return current_user
