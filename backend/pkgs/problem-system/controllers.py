"""
Core Domain Controllers (FastAPI Controllers)
コアドメインコントローラー (FastAPI コントローラー)

Author: Judge System Team
Date: 2025-01-12
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import logging

from fastapi import HTTPException, status
from pydantic import BaseModel, Field

from .services import (
    BookApplicationService,
    ProblemApplicationService,
    JudgeCaseApplicationService,
    UserProblemStatusApplicationService,
)
from ..domain.models import Book, Problem, JudgeCase, UserProblemStatus

logger = logging.getLogger(__name__)


# Request/Response Models
class BookResponse(BaseModel):
    """問題集レスポンスモデル"""

    id: UUID
    title: str
    author: str
    published_date: datetime
    is_published: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class ProblemResponse(BaseModel):
    """問題レスポンスモデル"""

    id: UUID
    title: str
    description: str
    book_id: Optional[UUID] = None
    difficulty: str
    estimated_time_minutes: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class ProblemDetailResponse(BaseModel):
    """問題詳細レスポンスモデル"""

    problem: ProblemResponse
    judge_cases: List[Dict[str, Any]]
    judge_case_count: int
    user_status: Optional[Dict[str, Any]] = None


class JudgeCaseResponse(BaseModel):
    """ジャッジケースレスポンスモデル"""

    id: UUID
    problem_id: UUID
    case_name: str
    input_data: str
    expected_output: str
    is_public: bool
    time_limit_ms: int
    memory_limit_mb: int


class UserStatusResponse(BaseModel):
    """ユーザーステータスレスポンスモデル"""

    user_id: str
    problem_id: UUID
    is_solved: bool
    score: Optional[int] = None
    attempt_count: int
    solved_at: Optional[datetime] = None
    created_at: datetime


class CreateBookRequest(BaseModel):
    """問題集作成リクエスト"""

    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    published_date: datetime
    is_published: bool = False


class CreateProblemRequest(BaseModel):
    """問題作成リクエスト"""

    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    book_id: Optional[UUID] = None
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")
    estimated_time_minutes: int = Field(default=30, ge=1, le=300)


class CreateJudgeCaseRequest(BaseModel):
    """ジャッジケース作成リクエスト"""

    case_name: str = Field(..., min_length=1, max_length=100)
    input_data: str
    expected_output: str
    is_public: bool = False
    time_limit_ms: int = Field(default=1000, ge=100, le=10000)
    memory_limit_mb: int = Field(default=128, ge=32, le=512)


class UpdateUserStatusRequest(BaseModel):
    """ユーザーステータス更新リクエスト"""

    is_solved: bool
    score: Optional[int] = Field(None, ge=0, le=100)


# Controllers
class BookController:
    """問題集コントローラー"""

    def __init__(self, book_service: BookApplicationService):
        self.book_service = book_service

    async def get_books(self) -> List[BookResponse]:
        """公開問題集一覧取得"""
        try:
            books = await self.book_service.get_published_books()
            return [
                BookResponse(
                    id=book.id,
                    title=book.title,
                    author=book.author,
                    published_date=book.published_date,
                    is_published=book.is_published,
                    created_at=book.created_at,
                    updated_at=book.updated_at,
                )
                for book in books
            ]
        except Exception as e:
            logger.error(f"Error in get_books: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="問題集の取得に失敗しました",
            )

    async def get_book(self, book_id: UUID) -> BookResponse:
        """問題集詳細取得"""
        try:
            book = await self.book_service.get_book_by_id(book_id)
            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="問題集が見つかりません",
                )

            return BookResponse(
                id=book.id,
                title=book.title,
                author=book.author,
                published_date=book.published_date,
                is_published=book.is_published,
                created_at=book.created_at,
                updated_at=book.updated_at,
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in get_book: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="問題集の取得に失敗しました",
            )

    async def create_book(self, request: CreateBookRequest) -> BookResponse:
        """問題集作成"""
        try:
            book = await self.book_service.create_book(
                title=request.title,
                author=request.author,
                published_date=request.published_date,
                is_published=request.is_published,
            )

            return BookResponse(
                id=book.id,
                title=book.title,
                author=book.author,
                published_date=book.published_date,
                is_published=book.is_published,
                created_at=book.created_at,
                updated_at=book.updated_at,
            )
        except Exception as e:
            logger.error(f"Error in create_book: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="問題集の作成に失敗しました",
            )


class ProblemController:
    """問題コントローラー"""

    def __init__(
        self,
        problem_service: ProblemApplicationService,
        user_status_service: UserProblemStatusApplicationService,
    ):
        self.problem_service = problem_service
        self.user_status_service = user_status_service

    async def get_problems(self, book_id: Optional[UUID] = None) -> List[ProblemResponse]:
        """公開問題一覧取得"""
        try:
            problems = await self.problem_service.get_published_problems(book_id)
            return [
                ProblemResponse(
                    id=problem.id,
                    title=problem.title,
                    description=problem.description,
                    book_id=problem.book_id,
                    difficulty=problem.difficulty,
                    estimated_time_minutes=problem.estimated_time_minutes,
                    status=problem.status,
                    created_at=problem.created_at,
                    updated_at=problem.updated_at,
                )
                for problem in problems
            ]
        except Exception as e:
            logger.error(f"Error in get_problems: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="問題一覧の取得に失敗しました",
            )

    async def get_problem(self, problem_id: UUID, user_id: Optional[str] = None) -> ProblemDetailResponse:
        """問題詳細取得"""
        try:
            problem_data = await self.problem_service.get_problem_with_judge_cases(problem_id)
            if not problem_data:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="問題が見つかりません")

            problem = problem_data["problem"]
            judge_cases = problem_data["judge_cases"]

            # 公開ケースのみをレスポンスに含める
            public_cases = [
                {
                    "id": str(case.id),
                    "case_name": case.case_name,
                    "input_data": case.input_data,
                    "expected_output": case.expected_output,
                    "time_limit_ms": case.time_limit_ms,
                    "memory_limit_mb": case.memory_limit_mb,
                }
                for case in judge_cases
                if case.is_public
            ]

            # ユーザーステータスを取得
            user_status = None
            if user_id:
                status = await self.user_status_service.get_user_status(user_id, problem_id)
                if status:
                    user_status = {
                        "is_solved": status.is_solved,
                        "score": status.score,
                        "attempt_count": status.attempt_count,
                        "solved_at": (status.solved_at.isoformat() if status.solved_at else None),
                    }

            return ProblemDetailResponse(
                problem=ProblemResponse(
                    id=problem.id,
                    title=problem.title,
                    description=problem.description,
                    book_id=problem.book_id,
                    difficulty=problem.difficulty,
                    estimated_time_minutes=problem.estimated_time_minutes,
                    status=problem.status,
                    created_at=problem.created_at,
                    updated_at=problem.updated_at,
                ),
                judge_cases=public_cases,
                judge_case_count=len(judge_cases),
                user_status=user_status,
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in get_problem: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="問題の取得に失敗しました",
            )

    async def create_problem(self, request: CreateProblemRequest) -> ProblemResponse:
        """問題作成"""
        try:
            problem = await self.problem_service.create_problem(
                title=request.title,
                description=request.description,
                book_id=request.book_id,
                difficulty=request.difficulty,
                estimated_time_minutes=request.estimated_time_minutes,
            )

            return ProblemResponse(
                id=problem.id,
                title=problem.title,
                description=problem.description,
                book_id=problem.book_id,
                difficulty=problem.difficulty,
                estimated_time_minutes=problem.estimated_time_minutes,
                status=problem.status,
                created_at=problem.created_at,
                updated_at=problem.updated_at,
            )
        except Exception as e:
            logger.error(f"Error in create_problem: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="問題の作成に失敗しました",
            )


class JudgeCaseController:
    """ジャッジケースコントローラー"""

    def __init__(self, judge_case_service: JudgeCaseApplicationService):
        self.judge_case_service = judge_case_service

    async def get_public_judge_cases(self, problem_id: UUID) -> List[JudgeCaseResponse]:
        """公開ジャッジケース取得"""
        try:
            judge_cases = await self.judge_case_service.get_public_judge_cases(problem_id)
            return [
                JudgeCaseResponse(
                    id=case.id,
                    problem_id=case.problem_id,
                    case_name=case.case_name,
                    input_data=case.input_data,
                    expected_output=case.expected_output,
                    is_public=case.is_public,
                    time_limit_ms=case.time_limit_ms,
                    memory_limit_mb=case.memory_limit_mb,
                )
                for case in judge_cases
            ]
        except Exception as e:
            logger.error(f"Error in get_public_judge_cases: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="ジャッジケースの取得に失敗しました",
            )

    async def create_judge_case(
        self, problem_id: UUID, request: CreateJudgeCaseRequest
    ) -> JudgeCaseResponse:
        """ジャッジケース作成"""
        try:
            judge_case = await self.judge_case_service.create_judge_case(
                problem_id=problem_id,
                case_name=request.case_name,
                input_data=request.input_data,
                expected_output=request.expected_output,
                is_public=request.is_public,
                time_limit_ms=request.time_limit_ms,
                memory_limit_mb=request.memory_limit_mb,
            )

            return JudgeCaseResponse(
                id=judge_case.id,
                problem_id=judge_case.problem_id,
                case_name=judge_case.case_name,
                input_data=judge_case.input_data,
                expected_output=judge_case.expected_output,
                is_public=judge_case.is_public,
                time_limit_ms=judge_case.time_limit_ms,
                memory_limit_mb=judge_case.memory_limit_mb,
            )
        except Exception as e:
            logger.error(f"Error in create_judge_case: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="ジャッジケースの作成に失敗しました",
            )


class UserStatusController:
    """ユーザーステータスコントローラー"""

    def __init__(self, user_status_service: UserProblemStatusApplicationService):
        self.user_status_service = user_status_service

    async def get_user_statuses(self, user_id: str) -> List[UserStatusResponse]:
        """ユーザーの全問題ステータス取得"""
        try:
            statuses = await self.user_status_service.get_user_all_statuses(user_id)
            return [
                UserStatusResponse(
                    user_id=status.user_id,
                    problem_id=status.problem_id,
                    is_solved=status.is_solved,
                    score=status.score,
                    attempt_count=status.attempt_count,
                    solved_at=status.solved_at,
                    created_at=status.created_at,
                )
                for status in statuses
            ]
        except Exception as e:
            logger.error(f"Error in get_user_statuses: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="ユーザーステータスの取得に失敗しました",
            )

    async def get_user_status(self, user_id: str, problem_id: UUID) -> Optional[UserStatusResponse]:
        """特定問題のユーザーステータス取得"""
        try:
            status = await self.user_status_service.get_user_status(user_id, problem_id)
            if not status:
                return None

            return UserStatusResponse(
                user_id=status.user_id,
                problem_id=status.problem_id,
                is_solved=status.is_solved,
                score=status.score,
                attempt_count=status.attempt_count,
                solved_at=status.solved_at,
                created_at=status.created_at,
            )
        except Exception as e:
            logger.error(f"Error in get_user_status: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="ユーザーステータスの取得に失敗しました",
            )

    async def update_user_status(
        self, user_id: str, problem_id: UUID, request: UpdateUserStatusRequest
    ) -> UserStatusResponse:
        """ユーザーステータス更新"""
        try:
            status = await self.user_status_service.update_user_status(
                user_id=user_id,
                problem_id=problem_id,
                is_solved=request.is_solved,
                score=request.score,
            )

            return UserStatusResponse(
                user_id=status.user_id,
                problem_id=status.problem_id,
                is_solved=status.is_solved,
                score=status.score,
                attempt_count=status.attempt_count,
                solved_at=status.solved_at,
                created_at=status.created_at,
            )
        except Exception as e:
            logger.error(f"Error in update_user_status: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="ユーザーステータスの更新に失敗しました",
            )
