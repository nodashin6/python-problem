"""
Core Domain API Routes
コアドメインAPIルート

Author: Judge System Team
Date: 2025-01-12
"""

from typing import List, Optional
from uuid import UUID
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr

from ..app.container import container
from ..app.controllers import (
    BookController,
    ProblemController,
    JudgeCaseController,
    UserStatusController,
    BookResponse,
    ProblemResponse,
    ProblemDetailResponse,
    JudgeCaseResponse,
    UserStatusResponse,
    CreateBookRequest,
    CreateProblemRequest,
    CreateJudgeCaseRequest,
    UpdateUserStatusRequest,
)
from ...shared.auth import (
    get_current_user,
    require_admin,
    User,
    get_optional_user,
    create_access_token,
    Role,
)
from ...const import UserRole

logger = logging.getLogger(__name__)

core_router = APIRouter(prefix="/core", tags=["core"])


# Dependency injection
async def get_book_controller() -> BookController:
    """問題集コントローラーを取得"""
    return BookController(container.book_service())


async def get_problem_controller() -> ProblemController:
    """問題コントローラーを取得"""
    return ProblemController(
        container.problem_service(), container.user_status_service()
    )


async def get_judge_case_controller() -> JudgeCaseController:
    """ジャッジケースコントローラーを取得"""
    return JudgeCaseController(container.judge_case_service())


async def get_user_status_controller() -> UserStatusController:
    """ユーザーステータスコントローラーを取得"""
    return UserStatusController(container.user_status_service())


# =============================================================================
# Book (問題集) エンドポイント
# =============================================================================


@core_router.get("/books", response_model=List[BookResponse])
async def get_books(controller: BookController = Depends(get_book_controller)):
    """
    公開されている問題集一覧を取得

    Returns:
        問題集一覧
    """
    return await controller.get_books()


@core_router.get("/books/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: UUID = Path(..., description="問題集ID"),
    controller: BookController = Depends(get_book_controller),
):
    """
    問題集詳細を取得

    Args:
        book_id: 問題集ID

    Returns:
        問題集詳細
    """
    return await controller.get_book(book_id)


@core_router.post(
    "/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED
)
async def create_book(
    request: CreateBookRequest,
    controller: BookController = Depends(get_book_controller),
    current_user: User = Depends(require_admin),
):
    """
    新しい問題集を作成 (管理者のみ)

    Args:
        request: 問題集作成リクエスト

    Returns:
        作成された問題集
    """
    return await controller.create_book(request)


# =============================================================================
# Problem (問題) エンドポイント
# =============================================================================


@core_router.get("/problems", response_model=List[ProblemResponse])
async def get_problems(
    book_id: Optional[UUID] = Query(None, description="問題集IDでフィルタリング"),
    controller: ProblemController = Depends(get_problem_controller),
):
    """
    公開されている問題一覧を取得

    Args:
        book_id: 問題集IDでフィルタリング (オプション)

    Returns:
        問題一覧
    """
    return await controller.get_problems(book_id)


@core_router.get("/problems/{problem_id}", response_model=ProblemDetailResponse)
async def get_problem(
    problem_id: UUID = Path(..., description="問題ID"),
    user_id: Optional[str] = Query(None, description="ユーザーID"),
    controller: ProblemController = Depends(get_problem_controller),
):
    """
    問題詳細を取得

    Args:
        problem_id: 問題ID
        user_id: ユーザーID (ユーザーステータス取得のため)

    Returns:
        問題詳細とジャッジケース情報
    """
    return await controller.get_problem(problem_id, user_id)


@core_router.post(
    "/problems", response_model=ProblemResponse, status_code=status.HTTP_201_CREATED
)
async def create_problem(
    request: CreateProblemRequest,
    controller: ProblemController = Depends(get_problem_controller),
    current_user: User = Depends(require_admin),
):
    """
    新しい問題を作成 (管理者のみ)

    Args:
        request: 問題作成リクエスト

    Returns:
        作成された問題
    """
    return await controller.create_problem(request)


# =============================================================================
# Judge Case (ジャッジケース) エンドポイント
# =============================================================================


@core_router.get(
    "/problems/{problem_id}/judge-cases", response_model=List[JudgeCaseResponse]
)
async def get_public_judge_cases(
    problem_id: UUID = Path(..., description="問題ID"),
    controller: JudgeCaseController = Depends(get_judge_case_controller),
):
    """
    問題の公開ジャッジケースを取得

    Args:
        problem_id: 問題ID

    Returns:
        公開ジャッジケース一覧
    """
    return await controller.get_public_judge_cases(problem_id)


@core_router.post(
    "/problems/{problem_id}/judge-cases",
    response_model=JudgeCaseResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_judge_case(
    problem_id: UUID = Path(..., description="問題ID"),
    request: CreateJudgeCaseRequest = ...,
    controller: JudgeCaseController = Depends(get_judge_case_controller),
    current_user: User = Depends(require_admin),
):
    """
    新しいジャッジケースを作成 (管理者のみ)

    Args:
        problem_id: 問題ID
        request: ジャッジケース作成リクエスト

    Returns:
        作成されたジャッジケース
    """
    return await controller.create_judge_case(problem_id, request)


# =============================================================================
# User Status (ユーザーステータス) エンドポイント
# =============================================================================


@core_router.get("/users/{user_id}/status", response_model=List[UserStatusResponse])
async def get_user_statuses(
    user_id: str = Path(..., description="ユーザーID"),
    controller: UserStatusController = Depends(get_user_status_controller),
    current_user: User = Depends(get_current_user),
):
    """
    ユーザーの全問題解決状況を取得

    Args:
        user_id: ユーザーID

    Returns:
        ユーザーの全問題解決状況
    """
    # 自分のステータスまたは管理者のみ取得可能
    if current_user.user_id != user_id and not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="他のユーザーのステータスを取得する権限がありません",
        )

    return await controller.get_user_statuses(user_id)


@core_router.get(
    "/users/{user_id}/status/{problem_id}", response_model=UserStatusResponse
)
async def get_user_status(
    user_id: str = Path(..., description="ユーザーID"),
    problem_id: UUID = Path(..., description="問題ID"),
    controller: UserStatusController = Depends(get_user_status_controller),
    current_user: User = Depends(get_current_user),
):
    """
    特定問題のユーザー解決状況を取得

    Args:
        user_id: ユーザーID
        problem_id: 問題ID

    Returns:
        ユーザーの特定問題解決状況
    """
    # 自分のステータスまたは管理者のみ取得可能
    if current_user.user_id != user_id and not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="他のユーザーのステータスを取得する権限がありません",
        )

    status_result = await controller.get_user_status(user_id, problem_id)
    if not status_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーステータスが見つかりません",
        )

    return status_result


@core_router.put(
    "/users/{user_id}/status/{problem_id}", response_model=UserStatusResponse
)
async def update_user_status(
    user_id: str = Path(..., description="ユーザーID"),
    problem_id: UUID = Path(..., description="問題ID"),
    request: UpdateUserStatusRequest = ...,
    controller: UserStatusController = Depends(get_user_status_controller),
    current_user: User = Depends(get_current_user),
):
    """
    ユーザーの問題解決状況を更新

    Args:
        user_id: ユーザーID
        problem_id: 問題ID
        request: ステータス更新リクエスト

    Returns:
        更新されたユーザーステータス
    """
    # 自分のステータスまたは管理者のみ更新可能
    if current_user.user_id != user_id and not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="他のユーザーのステータスを更新する権限がありません",
        )

    return await controller.update_user_status(user_id, problem_id, request)


# =============================================================================
# Authentication & User Management エンドポイント
# =============================================================================


class RegisterUserRequest(BaseModel):
    """ユーザー登録リクエスト"""

    email: EmailStr
    username: str
    password: str
    display_name: str = ""
    bio: str = ""
    avatar_url: str = ""


class LoginRequest(BaseModel):
    """ログインリクエスト"""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """ユーザー情報レスポンス"""

    id: str
    email: str
    username: str
    display_name: str
    bio: str
    avatar_url: str
    is_active: bool
    is_verified: bool
    role: str


class AuthResponse(BaseModel):
    """認証レスポンス"""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


@core_router.post(
    "/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(request: RegisterUserRequest):
    """
    新しいユーザーを登録

    Args:
        request: ユーザー登録リクエスト

    Returns:
        認証トークンとユーザー情報
    """
    try:
        user_service = container.user_service()

        # Register user using application service
        result = await user_service.register_user(
            email=request.email,
            username=request.username,
            password=request.password,
            display_name=request.display_name or request.username,
            bio=request.bio,
            avatar_url=request.avatar_url,
        )

        user_response = UserResponse(
            id=result["user"]["id"],
            email=result["user"]["email"],
            username=result["user"]["username"],
            display_name=result["user"]["display_name"],
            bio=request.bio,
            avatar_url=request.avatar_url,
            is_active=True,
            is_verified=False,
            role=result["user"]["role"],
        )

        return AuthResponse(access_token=result["access_token"], user=user_response)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to register user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@core_router.post("/auth/login", response_model=AuthResponse)
async def login_user(request: LoginRequest):
    """
    ユーザーログイン

    Args:
        request: ログインリクエスト

    Returns:
        認証トークンとユーザー情報
    """
    try:
        user_service = container.user_service()

        # Login user using application service
        result = await user_service.login_user(request.email, request.password)

        user_response = UserResponse(
            id=result["user"]["id"],
            email=result["user"]["email"],
            username=result["user"]["username"],
            display_name=result["user"]["display_name"],
            bio=None,  # Will be fetched from profile if needed
            avatar_url=None,  # Will be fetched from profile if needed
            is_active=True,
            is_verified=False,
            role=result["user"]["role"],
        )

        return AuthResponse(access_token=result["access_token"], user=user_response)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    except Exception as e:
        logger.error(f"Failed to login user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@core_router.get("/auth/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    現在のユーザー情報を取得

    Returns:
        ユーザー情報
    """
    try:
        user_service = container.user_service()
        profile_data = await user_service.get_user_profile(UUID(current_user.user_id))

        if not profile_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return UserResponse(
            id=profile_data["id"],
            email=profile_data["email"],
            username=profile_data["username"],
            display_name=profile_data["display_name"],
            bio=profile_data["bio"],
            avatar_url=profile_data["avatar_url"],
            is_active=profile_data["is_active"],
            is_verified=profile_data["is_verified"],
            role=profile_data["role"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


# =============================================================================
# Health Check エンドポイント
# =============================================================================


@core_router.get("/health")
async def health_check():
    """
    コアドメインヘルスチェック

    Returns:
        ステータス情報
    """
    return {
        "status": "ok",
        "domain": "core",
        "timestamp": "2025-01-12T00:00:00Z",
        "services": {
            "book_service": "ok",
            "problem_service": "ok",
            "judge_case_service": "ok",
            "user_status_service": "ok",
        },
    }
