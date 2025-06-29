"""
Core Domain API Routes
コアドメインAPIルート

Author: Judge System Team
Date: 2025-01-12
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr

from ..app.container import container
from ..app.controllers import (
    BookController,
    BookResponse,
    CreateBookRequest,
    CreateProblemRequest,
    ProblemController,
    ProblemDetailResponse,
    ProblemResponse,
)

logger = logging.getLogger(__name__)

core_router = APIRouter(prefix="/core", tags=["core"])


# Dependency injection
async def get_book_controller() -> BookController:
    """問題集コントローラーを取得"""
    return BookController(container.book_service())


async def get_problem_controller() -> ProblemController:
    """問題コントローラーを取得"""
    return ProblemController(container.problem_service())


# Authentication placeholders (外部パッケージで実装される予定)
async def get_current_user():
    """現在のユーザーを取得 (プレースホルダー)"""
    # TODO: 認証システムから実装を取得
    raise HTTPException(status_code=501, detail="Authentication not implemented")


async def require_admin():
    """管理者権限を要求 (プレースホルダー)"""
    # TODO: 認証システムから実装を取得
    raise HTTPException(status_code=501, detail="Authentication not implemented")


# =============================================================================
# Book (問題集) エンドポイント
# =============================================================================


@core_router.get("/books", response_model=list[BookResponse])
async def get_books(
    controller: BookController = Depends(get_book_controller),
):
    """
    公開されている問題集一覧を取得

    Returns:
        公開問題集一覧
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
    try:
        return await controller.get_book(book_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="問題集が見つかりません",
        ) from e


@core_router.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    request: CreateBookRequest,
    controller: BookController = Depends(get_book_controller),
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


@core_router.get("/problems", response_model=list[ProblemResponse])
async def get_problems(
    book_id: UUID | None = Query(None, description="問題集IDでフィルタリング"),
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
    user_id: str | None = Query(None, description="ユーザーID"),
    controller: ProblemController = Depends(get_problem_controller),
):
    """
    問題詳細を取得

    Args:
        problem_id: 問題ID
        user_id: ユーザーID (オプション)

    Returns:
        問題詳細
    """
    try:
        return await controller.get_problem(problem_id, user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="問題が見つかりません",
        ) from e


@core_router.post("/problems", response_model=ProblemResponse, status_code=status.HTTP_201_CREATED)
async def create_problem(
    request: CreateProblemRequest,
    controller: ProblemController = Depends(get_problem_controller),
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
        "timestamp": "2025-06-14T00:00:00Z",
        "services": {
            "book_service": "ok",
            "problem_service": "ok",
        },
    }
