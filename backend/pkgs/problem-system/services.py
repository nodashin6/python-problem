"""
Core Domain Application Services
コアドメインアプリケーションサービス

Author: Judge System Team
Date: 2025-01-12
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
import logging
from datetime import datetime

from ..domain.models import (
    Book,
    Problem,
    JudgeCase,
    UserProblemStatus,
    User,
    UserProfile,
)
from ....auth.user_service import UserDomainService
from ..infra.repositories.interfaces import (
    BookRepositoryInterface,
    ProblemRepositoryInterface,
    JudgeCaseRepositoryInterface,
    UserProblemStatusRepositoryInterface,
)
from ...const import UserRole

logger = logging.getLogger(__name__)


class BookApplicationService:
    """問題集管理アプリケーションサービス"""

    def __init__(self, book_repository: BookRepositoryInterface):
        self.book_repository = book_repository

    async def get_published_books(self) -> List[Book]:
        """公開されている問題集一覧を取得"""
        try:
            books = await self.book_repository.find_published_books()
            logger.info(f"Retrieved {len(books)} published books")
            return books
        except Exception as e:
            logger.error(f"Error getting published books: {e}")
            raise

    async def get_book_by_id(self, book_id: UUID) -> Optional[Book]:
        """問題集をIDで取得"""
        try:
            book = await self.book_repository.find_by_id(book_id)
            if book:
                logger.info(f"Book found: {book.title}")
            else:
                logger.warning(f"Book not found: {book_id}")
            return book
        except Exception as e:
            logger.error(f"Error getting book by ID {book_id}: {e}")
            raise

    async def create_book(
        self,
        title: str,
        author: str,
        published_date: datetime,
        is_published: bool = False,
    ) -> Book:
        """新しい問題集を作成"""
        try:
            book = Book(
                title=title,
                author=author,
                published_date=published_date,
                is_published=is_published,
            )
            created_book = await self.book_repository.create(book)
            logger.info(f"Book created: {created_book.title}")
            return created_book
        except Exception as e:
            logger.error(f"Error creating book: {e}")
            raise


class ProblemApplicationService:
    """問題管理アプリケーションサービス"""

    def __init__(
        self,
        problem_repository: ProblemRepositoryInterface,
        judge_case_repository: JudgeCaseRepositoryInterface,
    ):
        self.problem_repository = problem_repository
        self.judge_case_repository = judge_case_repository

    async def get_published_problems(self, book_id: Optional[UUID] = None) -> List[Problem]:
        """公開されている問題一覧を取得"""
        try:
            if book_id:
                problems = await self.problem_repository.find_by_book_id(book_id)
                # 公開されているもののみフィルタリング
                problems = [p for p in problems if p.status == "published"]
            else:
                problems = await self.problem_repository.find_published_problems()

            logger.info(f"Retrieved {len(problems)} published problems")
            return problems
        except Exception as e:
            logger.error(f"Error getting published problems: {e}")
            raise

    async def get_problem_by_id(self, problem_id: UUID) -> Optional[Problem]:
        """問題をIDで取得"""
        try:
            problem = await self.problem_repository.find_by_id(problem_id)
            if problem:
                logger.info(f"Problem found: {problem.title}")
            else:
                logger.warning(f"Problem not found: {problem_id}")
            return problem
        except Exception as e:
            logger.error(f"Error getting problem by ID {problem_id}: {e}")
            raise

    async def get_problem_with_judge_cases(self, problem_id: UUID) -> Optional[Dict[str, Any]]:
        """問題とそのジャッジケースを取得"""
        try:
            problem = await self.problem_repository.find_by_id(problem_id)
            if not problem:
                return None

            judge_cases = await self.judge_case_repository.find_by_problem_id(problem_id)

            result = {
                "problem": problem,
                "judge_cases": judge_cases,
                "judge_case_count": len(judge_cases),
            }

            logger.info(f"Problem with {len(judge_cases)} judge cases retrieved: {problem.title}")
            return result

        except Exception as e:
            logger.error(f"Error getting problem with judge cases {problem_id}: {e}")
            raise

    async def create_problem(
        self,
        title: str,
        description: str,
        book_id: Optional[UUID] = None,
        difficulty: str = "medium",
        estimated_time_minutes: int = 30,
    ) -> Problem:
        """新しい問題を作成"""
        try:
            problem = Problem(
                title=title,
                description=description,
                book_id=book_id,
                difficulty=difficulty,
                estimated_time_minutes=estimated_time_minutes,
                status="draft",
            )
            created_problem = await self.problem_repository.create(problem)
            logger.info(f"Problem created: {created_problem.title}")
            return created_problem
        except Exception as e:
            logger.error(f"Error creating problem: {e}")
            raise


class JudgeCaseApplicationService:
    """ジャッジケース管理アプリケーションサービス"""

    def __init__(self, judge_case_repository: JudgeCaseRepositoryInterface):
        self.judge_case_repository = judge_case_repository

    async def get_judge_cases_by_problem(self, problem_id: UUID) -> List[JudgeCase]:
        """問題のジャッジケース一覧を取得"""
        try:
            judge_cases = await self.judge_case_repository.find_by_problem_id(problem_id)
            logger.info(f"Retrieved {len(judge_cases)} judge cases for problem {problem_id}")
            return judge_cases
        except Exception as e:
            logger.error(f"Error getting judge cases for problem {problem_id}: {e}")
            raise

    async def get_public_judge_cases(self, problem_id: UUID) -> List[JudgeCase]:
        """公開ジャッジケースのみを取得"""
        try:
            all_cases = await self.judge_case_repository.find_by_problem_id(problem_id)
            public_cases = [case for case in all_cases if case.is_public]
            logger.info(f"Retrieved {len(public_cases)} public judge cases for problem {problem_id}")
            return public_cases
        except Exception as e:
            logger.error(f"Error getting public judge cases for problem {problem_id}: {e}")
            raise

    async def create_judge_case(
        self,
        problem_id: UUID,
        case_name: str,
        input_data: str,
        expected_output: str,
        is_public: bool = False,
        time_limit_ms: int = 1000,
        memory_limit_mb: int = 128,
    ) -> JudgeCase:
        """新しいジャッジケースを作成"""
        try:
            judge_case = JudgeCase(
                problem_id=problem_id,
                case_name=case_name,
                input_data=input_data,
                expected_output=expected_output,
                is_public=is_public,
                time_limit_ms=time_limit_ms,
                memory_limit_mb=memory_limit_mb,
            )
            created_case = await self.judge_case_repository.create(judge_case)
            logger.info(f"Judge case created: {created_case.case_name}")
            return created_case
        except Exception as e:
            logger.error(f"Error creating judge case: {e}")
            raise


class UserProblemStatusApplicationService:
    """ユーザー問題解決状況管理アプリケーションサービス"""

    def __init__(self, user_problem_status_repository: UserProblemStatusRepositoryInterface):
        self.user_problem_status_repository = user_problem_status_repository

    async def get_user_status(self, user_id: str, problem_id: UUID) -> Optional[UserProblemStatus]:
        """ユーザーの特定問題に対する解決状況を取得"""
        try:
            status = await self.user_problem_status_repository.find_by_user_and_problem(user_id, problem_id)
            if status:
                logger.info(f"User status found for {user_id}, problem {problem_id}")
            return status
        except Exception as e:
            logger.error(f"Error getting user status for {user_id}, problem {problem_id}: {e}")
            raise

    async def get_user_all_statuses(self, user_id: str) -> List[UserProblemStatus]:
        """ユーザーの全問題解決状況を取得"""
        try:
            statuses = await self.user_problem_status_repository.find_by_user_id(user_id)
            logger.info(f"Retrieved {len(statuses)} problem statuses for user {user_id}")
            return statuses
        except Exception as e:
            logger.error(f"Error getting all statuses for user {user_id}: {e}")
            raise

    async def update_user_status(
        self,
        user_id: str,
        problem_id: UUID,
        is_solved: bool,
        score: Optional[int] = None,
    ) -> UserProblemStatus:
        """ユーザーの問題解決状況を更新"""
        try:
            # 既存のステータスを取得
            existing_status = await self.user_problem_status_repository.find_by_user_and_problem(
                user_id, problem_id
            )

            if existing_status:
                # 更新
                existing_status.is_solved = is_solved
                existing_status.score = score
                existing_status.attempt_count += 1
                if is_solved:
                    existing_status.solved_at = datetime.utcnow()

                updated_status = await self.user_problem_status_repository.update(existing_status)
                logger.info(f"User status updated for {user_id}, problem {problem_id}")
                return updated_status
            else:
                # 新規作成
                new_status = UserProblemStatus(
                    user_id=user_id,
                    problem_id=problem_id,
                    is_solved=is_solved,
                    score=score,
                    attempt_count=1,
                    solved_at=datetime.utcnow() if is_solved else None,
                )
                created_status = await self.user_problem_status_repository.create(new_status)
                logger.info(f"User status created for {user_id}, problem {problem_id}")
                return created_status

        except Exception as e:
            logger.error(f"Error updating user status for {user_id}, problem {problem_id}: {e}")
            raise


class UserApplicationService:
    """ユーザー管理アプリケーションサービス"""

    def __init__(self, user_service: UserDomainService):
        self.user_service = user_service

    async def register_user(
        self,
        email: str,
        username: str,
        password: str,
        display_name: str,
        bio: Optional[str] = None,
        avatar_url: Optional[str] = None,
        github_username: Optional[str] = None,
        preferred_language: str = "python",
    ) -> Dict[str, Any]:
        """新規ユーザー登録"""
        try:
            # プロフィール作成
            profile = UserProfile(
                display_name=display_name,
                bio=bio,
                avatar_url=avatar_url,
                github_username=github_username,
                preferred_language=preferred_language,
            )

            # ユーザー登録
            user = await self.user_service.register_user(
                email=email,
                username=username,
                password=password,
                profile=profile,
                role=UserRole.USER,
            )

            # JWTトークン生成
            access_token = await self.user_service.create_access_token(user)
            refresh_token = await self.user_service.create_refresh_token(user)

            logger.info(f"User registered successfully: {username}")
            return {
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "username": user.username,
                    "display_name": user.profile.display_name,
                    "role": user.role.value,
                },
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }

        except Exception as e:
            logger.error(f"Error registering user {username}: {e}")
            raise

    async def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """ユーザーログイン"""
        try:
            # 認証
            user = await self.user_service.authenticate_user(email, password)
            if not user:
                raise ValueError("Invalid email or password")

            # JWTトークン生成
            access_token = await self.user_service.create_access_token(user)
            refresh_token = await self.user_service.create_refresh_token(user)

            logger.info(f"User logged in successfully: {user.username}")
            return {
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "username": user.username,
                    "display_name": user.profile.display_name,
                    "role": user.role.value,
                },
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }

        except Exception as e:
            logger.error(f"Error logging in user with email {email}: {e}")
            raise

    async def get_user_profile(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """ユーザープロフィール取得"""
        try:
            user = await self.user_service.get_user_by_id(user_id)
            if not user:
                return None

            return {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "display_name": user.profile.display_name,
                "bio": user.profile.bio,
                "avatar_url": user.profile.avatar_url,
                "github_username": user.profile.github_username,
                "preferred_language": user.profile.preferred_language,
                "role": user.role.value,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "created_at": user.created_at.isoformat(),
                "last_login_at": (user.last_login_at.isoformat() if user.last_login_at else None),
            }

        except Exception as e:
            logger.error(f"Error getting user profile for {user_id}: {e}")
            raise

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """アクセストークンリフレッシュ"""
        try:
            # リフレッシュトークンから新しいアクセストークンを生成
            new_access_token = await self.user_service.refresh_access_token(refresh_token)

            logger.info("Access token refreshed successfully")
            return {
                "access_token": new_access_token,
                "token_type": "bearer",
            }

        except Exception as e:
            logger.error(f"Error refreshing access token: {e}")
            raise
