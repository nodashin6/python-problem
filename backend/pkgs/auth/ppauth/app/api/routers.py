"""
Authentication API endpoints
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from ...domain.entities.enums import UserRole
from ...domain.models.user import User
from ...domain.services.auth_service import AuthenticationService
from ...domain.services.user_service import UserService
from ...usecase.create_user_usecase import CreateUserCommand, CreateUserUseCase
from ..dependencies import (
    get_auth_service,
    get_current_user,
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
    role: str
    is_active: bool
    created_at: str


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
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Generate access token
        access_token = auth_service.create_access_token(user)

        # Get user role for response
        user_role = await user_service.get_user_role(user.id)
        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User role not found"
            )

        return TokenResponse(
            access_token=access_token,
            user={
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "role": user_role.role.value,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed") from e


@auth_router.post("/register", response_model=UserResponse)
async def register(
    request: RegisterRequest,
    create_user_use_case: CreateUserUseCase = Depends(),
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
        )

        user = await create_user_use_case.execute(command)

        return UserResponse(
            id=str(user.id),
            username=user.username,
            display_name=user.display_name,
            email=user.email,
            avatar_url=user.avatar_url,
            bio=user.bio,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed"
        ) from e


@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get current user profile"""
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        display_name=current_user.display_name,
        email=current_user.email,
        avatar_url=current_user.avatar_url,
        bio=current_user.bio,
        role=current_user.role.value,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat(),
    )


@auth_router.get("/users", response_model=list[UserResponse])
async def list_users(
    _: User = Depends(require_admin),
    user_service: UserService = Depends(get_user_service),
) -> list[UserResponse]:
    """List all users (admin only)"""
    try:
        users = await user_service.list_users()

        return [
            UserResponse(
                id=str(user.id),
                username=user.username,
                display_name=user.display_name,
                email=user.email,
                avatar_url=user.avatar_url,
                bio=user.bio,
                role=user.role.value,
                is_active=user.is_active,
                created_at=user.created_at.isoformat(),
            )
            for user in users
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch users"
        ) from e


@auth_router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    _: User = Depends(require_admin),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Get user by ID (admin only)"""
    try:
        from uuid import UUID

        user = await user_service.get_user(UUID(user_id))

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return UserResponse(
            id=str(user.id),
            username=user.username,
            display_name=user.display_name,
            email=user.email,
            avatar_url=user.avatar_url,
            bio=user.bio,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format") from e
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch user"
        ) from e


@auth_router.post("/logout")
async def logout(_: User = Depends(get_current_user)) -> dict[str, str]:
    """User logout endpoint"""
    # JWTトークンはステートレスなので、クライアント側でトークンを破棄するだけ
    # 必要に応じてトークンブラックリスト機能を実装可能
    return {"message": "Successfully logged out"}


@auth_router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy", "service": "ppauth"}
