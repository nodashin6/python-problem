"""
Authentication API endpoints
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr

from ...domain.enums import UserRole
from ...domain.models.user import User
from ...domain.services.auth_service import AuthenticationService
from ...domain.services.user_service import UserService
from ...usecase.create_user_usecase import CreateUserCommand, CreateUserUseCase
from ...usecase.delete_user_usecase import DeleteUserCommand, DeleteUserUseCase
from ...usecase.read_user_aggregate_usecase import ReadActiveUsersCommand, ReadActiveUsersUseCase
from ...usecase.read_user_by_email_usecase import ReadUserByEmailCommand, ReadUserByEmailUseCase
from ...usecase.read_user_by_id_usecase import ReadUserByIdCommand, ReadUserByIdUseCase
from ...usecase.read_users_by_role_usecase import ReadUsersByRoleCommand, ReadUsersByRoleUseCase
from ...usecase.update_user_usecase import UpdateUserCommand, UpdateUserUseCase
from ..dependencies import (
    get_auth_service,
    get_create_user_usecase,
    get_current_user,
    get_delete_user_usecase,
    get_read_active_users_usecase,
    get_read_user_by_email_usecase,
    get_read_user_by_id_usecase,
    get_read_users_by_role_usecase,
    get_update_user_usecase,
    get_user_service,
    require_admin,
)

auth_router = APIRouter(prefix="/auth", tags=["pp_auth"])


# Request/Response models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    username: str
    display_name: str
    email: EmailStr
    password: str
    avatar_url: str | None = None
    bio: str | None = None


class UpdateUserRequest(BaseModel):
    username: str | None = None
    display_name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    is_active: bool | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    id: str
    username: str
    display_name: str
    email: str
    avatar_url: str | None = None
    bio: str | None = None
    role: UserRole
    is_active: bool
    created_at: str


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total_count: int


class DeleteUserResponse(BaseModel):
    user_id: str
    deleted: bool
    soft_deleted: bool
    message: str


# Authentication endpoints
@auth_router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    auth_service: AuthenticationService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
) -> TokenResponse:
    """User login endpoint"""
    try:
        # Authenticate user
        user = await auth_service.authenticate_user(request.email, request.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Generate token
        access_token = auth_service.create_access_token(data={"sub": str(user.id), "email": user.email})

        return TokenResponse(
            access_token=access_token,
            user={
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "role": "USER",  # UserEntityにはroleがないのでデフォルト値を使用
            },
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {err!s}",
        ) from err


@auth_router.post("/register", response_model=UserResponse)
async def register(
    request: RegisterRequest,
    create_user_usecase: CreateUserUseCase = Depends(get_create_user_usecase),
) -> UserResponse:
    """User registration endpoint"""
    try:
        command = CreateUserCommand(
            username=request.username,
            display_name=request.display_name,
            email=request.email,
            password=request.password,
            avatar_url=request.avatar_url,
            bio=request.bio,
            role=UserRole.USER,  # 新規登録は通常ユーザーとして作成
        )

        result = await create_user_usecase.execute(command)

        return UserResponse(
            id=str(result.user_id),
            username=result.username,
            display_name=result.display_name,
            email=result.email,
            avatar_url=result.avatar_url,
            bio=result.bio,
            role=UserRole.USER.value,
            is_active=result.is_active,
            created_at="",  # TODO: 作成日時を取得
        )

    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {err!s}",
        ) from err


# User management endpoints
@auth_router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get current user information"""
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        display_name=current_user.display_name,
        email=current_user.email,
        avatar_url=current_user.avatar_url,
        bio=current_user.bio,
        role=current_user.role.value,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat() if current_user.created_at else "",
    )


@auth_router.get("/users/active", response_model=list[UserResponse])
async def get_active_users(
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
    offset: int = Query(0, ge=0, description="Number of users to skip"),
    read_active_users_usecase: ReadActiveUsersUseCase = Depends(get_read_active_users_usecase),
    current_user: User = Depends(require_admin),  # 管理者のみアクセス可能
) -> list[UserResponse]:
    """Get active users - Admin only"""
    try:
        command = ReadActiveUsersCommand(limit=limit, offset=offset)
        users = await read_active_users_usecase.execute(command)

        return [
            UserResponse(
                id=str(user.id),
                username=user.username,
                display_name=user.display_name,
                email=user.email,
                avatar_url=user.avatar_url,
                bio=user.bio,
                role=user.role.value if hasattr(user, "role") else UserRole.USER.value,
                is_active=user.is_active,
                created_at=user.created_at.isoformat() if user.created_at else "",
            )
            for user in users
        ]

    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get active users: {err!s}",
        ) from err


@auth_router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: UUID,
    read_user_usecase: ReadUserByIdUseCase = Depends(get_read_user_by_id_usecase),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get user by ID - Admin only or self"""
    try:
        # 管理者または自分自身の情報のみ取得可能
        if current_user.role != UserRole.ADMIN and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this user's information",
            )

        command = ReadUserByIdCommand(user_id=user_id)
        result = await read_user_usecase.execute(command)

        user = result.user  # UserResult -> UserEntity
        return UserResponse(
            id=str(user.id),
            username=user.username,
            display_name=user.display_name,
            email=user.email,
            avatar_url=user.avatar_url,
            bio=user.bio,
            role=user.role.value if hasattr(user, "role") else UserRole.USER.value,
            is_active=user.is_active,
            created_at=user.created_at.isoformat() if user.created_at else "",
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found: {err!s}",
        ) from err


@auth_router.get("/users", response_model=UserListResponse)
async def get_users_by_role(
    role: UserRole = Query(UserRole.USER, description="User role to filter by"),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
    offset: int = Query(0, ge=0, description="Number of users to skip"),
    read_users_usecase: ReadUsersByRoleUseCase = Depends(get_read_users_by_role_usecase),
    current_user: User = Depends(require_admin),  # 管理者のみアクセス可能
) -> UserListResponse:
    """Get users by role - Admin only"""
    try:
        command = ReadUsersByRoleCommand(
            role=role,
            limit=limit,
            offset=offset,
        )
        result = await read_users_usecase.execute(command)

        users = []
        for user_result in result.users:
            user = user_result.user  # UserResult -> UserEntity
            users.append(
                UserResponse(
                    id=str(user.id),
                    username=user.username,
                    display_name=user.display_name,
                    email=user.email,
                    avatar_url=user.avatar_url,
                    bio=user.bio,
                    role=user.role.value if hasattr(user, "role") else role.value,
                    is_active=user.is_active,
                    created_at=user.created_at.isoformat() if user.created_at else "",
                )
            )

        return UserListResponse(
            users=users,
            total_count=result.total_count,
        )

    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get users: {err!s}",
        ) from err


@auth_router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    request: UpdateUserRequest,
    update_user_usecase: UpdateUserUseCase = Depends(get_update_user_usecase),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Update user - Admin or self only"""
    try:
        # 管理者または自分自身の情報のみ更新可能
        if current_user.role != UserRole.ADMIN and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this user",
            )

        command = UpdateUserCommand(
            user_id=user_id,
            username=request.username,
            display_name=request.display_name,
            email=request.email,
            password=request.password,
            avatar_url=request.avatar_url,
            bio=request.bio,
            is_active=request.is_active,
        )

        result = await update_user_usecase.execute(command)

        return UserResponse(
            id=str(result.user_id),
            username=result.username,
            display_name=result.display_name,
            email=result.email,
            avatar_url=result.avatar_url,
            bio=result.bio,
            role=UserRole.USER.value,  # TODO: ロール情報も返すように改善
            is_active=result.is_active,
            created_at="",  # TODO: 作成日時を取得
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update user: {err!s}",
        ) from err


@auth_router.delete("/users/{user_id}", response_model=DeleteUserResponse)
async def delete_user(
    user_id: UUID,
    soft_delete: bool = Query(True, description="Soft delete (deactivate) or hard delete"),
    delete_user_usecase: DeleteUserUseCase = Depends(get_delete_user_usecase),
    current_user: User = Depends(require_admin),  # 管理者のみ削除可能
) -> DeleteUserResponse:
    """Delete user - Admin only"""
    try:
        command = DeleteUserCommand(
            user_id=user_id,
            soft_delete=soft_delete,
        )

        result = await delete_user_usecase.execute(command)

        message = "User deactivated successfully" if result.soft_deleted else "User deleted successfully"

        return DeleteUserResponse(
            user_id=str(result.user_id),
            deleted=result.deleted,
            soft_deleted=result.soft_deleted,
            message=message,
        )

    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete user: {err!s}",
        ) from err


# Admin-only user creation endpoint
@auth_router.post("/admin/users", response_model=UserResponse)
async def create_user_admin(
    request: RegisterRequest,
    role: UserRole = Query(UserRole.USER, description="Role for the new user"),
    create_user_usecase: CreateUserUseCase = Depends(get_create_user_usecase),
    current_user: User = Depends(require_admin),  # 管理者のみアクセス可能
) -> UserResponse:
    """Create user as admin - can set any role"""
    try:
        command = CreateUserCommand(
            username=request.username,
            display_name=request.display_name,
            email=request.email,
            password=request.password,
            avatar_url=request.avatar_url,
            bio=request.bio,
            role=role,
        )

        result = await create_user_usecase.execute(command)

        return UserResponse(
            id=str(result.user_id),
            username=result.username,
            display_name=result.display_name,
            email=result.email,
            avatar_url=result.avatar_url,
            bio=result.bio,
            role=role.value,
            is_active=result.is_active,
            created_at="",  # TODO: 作成日時を取得
        )

    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create user: {err!s}",
        ) from err
