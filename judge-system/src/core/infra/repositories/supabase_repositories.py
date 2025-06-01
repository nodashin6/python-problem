"""
Core Domain Supabase Repository Implementations
コアドメインSupabaseリポジトリ実装

Author: Judge System Team
Date: 2025-01-12
"""

from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
import logging
from datetime import datetime

from supabase import AsyncClient

from .interfaces import (
    BookRepositoryInterface,
    ProblemRepositoryInterface,
    JudgeCaseRepositoryInterface,
    # UserProblemStatusRepositoryInterface,  # TODO: 未実装のため一時コメントアウト
)
from ...domain.models import Book, Problem, JudgeCase

logger = logging.getLogger(__name__)


class BaseSupabaseRepository:
    """Base class for Supabase repositories"""

    def __init__(self, supabase_client: AsyncClient):
        self.supabase = supabase_client

    async def _handle_error(self, error: Exception, operation: str) -> None:
        """Handle repository errors with logging"""
        logger.error(f"Core repository error in {operation}: {str(error)}")
        raise


class SupabaseBookRepository(BaseSupabaseRepository, BookRepositoryInterface):
    """Supabase implementation of Book repository for Core domain"""

    async def create(self, book: Book) -> Book:
        """Create a new book"""
        try:
            data = {
                "title": book.title,
                "author": book.author,
                "published_date": book.published_date.isoformat(),
                "is_published": book.is_published,
            }

            # IDが設定されていない場合は生成
            if book.id:
                data["id"] = str(book.id)

            result = await self.supabase.table("books").insert(data).execute()

            if result.data:
                return Book(**result.data[0])
            raise Exception("Failed to create book")

        except Exception as e:
            await self._handle_error(e, "create book")

    async def find_by_id(self, book_id: UUID) -> Optional[Book]:
        """Find book by ID"""
        try:
            result = (
                await self.supabase.table("books")
                .select("*")
                .eq("id", str(book_id))
                .execute()
            )

            if result.data:
                return Book(**result.data[0])
            return None

        except Exception as e:
            await self._handle_error(e, f"find book {book_id}")

    async def find_published_books(self) -> List[Book]:
        """Find all published books"""
        try:
            result = (
                await self.supabase.table("books")
                .select("*")
                .eq("is_published", True)
                .execute()
            )

            return [Book(**book) for book in result.data] if result.data else []

        except Exception as e:
            await self._handle_error(e, "find published books")

    async def update(self, book: Book) -> Book:
        """Update book"""
        try:
            result = (
                await self.supabase.table("books")
                .update(
                    {
                        "title": book.title,
                        "author": book.author,
                        "published_date": book.published_date.isoformat(),
                        "is_published": book.is_published,
                    }
                )
                .eq("id", str(book.id))
                .execute()
            )

            if result.data:
                return Book(**result.data[0])
            raise Exception("Failed to update book")

        except Exception as e:
            await self._handle_error(e, f"update book {book.id}")

    async def delete(self, book_id: UUID) -> bool:
        """Delete book"""
        try:
            result = (
                await self.supabase.table("books")
                .delete()
                .eq("id", str(book_id))
                .execute()
            )
            return len(result.data) > 0 if result.data else False

        except Exception as e:
            await self._handle_error(e, f"delete book {book_id}")


class SupabaseProblemRepository(BaseSupabaseRepository, ProblemRepositoryInterface):
    """Supabase implementation of Problem repository for Core domain"""

    async def create(self, problem: Problem) -> Problem:
        """Create a new problem"""
        try:
            data = {
                "title": problem.title,
                "description": problem.description,
                "book_id": str(problem.book_id) if problem.book_id else None,
                "difficulty": problem.difficulty,
                "estimated_time_minutes": problem.estimated_time_minutes,
                "status": problem.status,
            }

            # IDが設定されていない場合は生成
            if problem.id:
                data["id"] = str(problem.id)

            result = await self.supabase.table("problems").insert(data).execute()

            if result.data:
                return Problem(**result.data[0])
            raise Exception("Failed to create problem")

        except Exception as e:
            await self._handle_error(e, "create problem")

    async def find_by_id(self, problem_id: UUID) -> Optional[Problem]:
        """Find problem by ID"""
        try:
            result = (
                await self.supabase.table("problems")
                .select("*")
                .eq("id", str(problem_id))
                .execute()
            )

            if result.data:
                return Problem(**result.data[0])
            return None

        except Exception as e:
            await self._handle_error(e, f"find problem {problem_id}")

    async def find_by_book_id(self, book_id: UUID) -> List[Problem]:
        """Find problems by book ID"""
        try:
            result = (
                await self.supabase.table("problems")
                .select("*")
                .eq("book_id", str(book_id))
                .execute()
            )

            return (
                [Problem(**problem) for problem in result.data] if result.data else []
            )

        except Exception as e:
            await self._handle_error(e, f"find problems by book {book_id}")

    async def find_published_problems(self) -> List[Problem]:
        """Find all published problems"""
        try:
            result = (
                await self.supabase.table("problems")
                .select("*")
                .eq("status", "published")
                .execute()
            )

            return (
                [Problem(**problem) for problem in result.data] if result.data else []
            )

        except Exception as e:
            await self._handle_error(e, "find published problems")

    async def update(self, problem: Problem) -> Problem:
        """Update problem"""
        try:
            result = (
                await self.supabase.table("problems")
                .update(
                    {
                        "title": problem.title,
                        "description": problem.description,
                        "book_id": str(problem.book_id) if problem.book_id else None,
                        "difficulty": problem.difficulty,
                        "estimated_time_minutes": problem.estimated_time_minutes,
                        "status": problem.status,
                    }
                )
                .eq("id", str(problem.id))
                .execute()
            )

            if result.data:
                return Problem(**result.data[0])
            raise Exception("Failed to update problem")

        except Exception as e:
            await self._handle_error(e, f"update problem {problem.id}")

    async def delete(self, problem_id: UUID) -> bool:
        """Delete problem"""
        try:
            result = (
                await self.supabase.table("problems")
                .delete()
                .eq("id", str(problem_id))
                .execute()
            )
            return len(result.data) > 0 if result.data else False

        except Exception as e:
            await self._handle_error(e, f"delete problem {problem_id}")


class SupabaseJudgeCaseRepository(BaseSupabaseRepository, JudgeCaseRepositoryInterface):
    """Supabase implementation of JudgeCase repository for Core domain"""

    async def create(self, judge_case: JudgeCase) -> JudgeCase:
        """Create a new judge case"""
        try:
            data = {
                "problem_id": str(judge_case.problem_id),
                "case_name": judge_case.case_name,
                "input_data": judge_case.input_data,
                "expected_output": judge_case.expected_output,
                "is_public": judge_case.is_public,
                "time_limit_ms": judge_case.time_limit_ms,
                "memory_limit_mb": judge_case.memory_limit_mb,
            }

            # IDが設定されていない場合は生成
            if judge_case.id:
                data["id"] = str(judge_case.id)

            result = await self.supabase.table("judge_cases").insert(data).execute()

            if result.data:
                return JudgeCase(**result.data[0])
            raise Exception("Failed to create judge case")

        except Exception as e:
            await self._handle_error(e, "create judge case")

    async def find_by_id(self, judge_case_id: UUID) -> Optional[JudgeCase]:
        """Find judge case by ID"""
        try:
            result = (
                await self.supabase.table("judge_cases")
                .select("*")
                .eq("id", str(judge_case_id))
                .execute()
            )

            if result.data:
                return JudgeCase(**result.data[0])
            return None

        except Exception as e:
            await self._handle_error(e, f"find judge case {judge_case_id}")

    async def find_by_problem_id(self, problem_id: UUID) -> List[JudgeCase]:
        """Find judge cases by problem ID"""
        try:
            result = (
                await self.supabase.table("judge_cases")
                .select("*")
                .eq("problem_id", str(problem_id))
                .execute()
            )

            return [JudgeCase(**case) for case in result.data] if result.data else []

        except Exception as e:
            await self._handle_error(e, f"find judge cases by problem {problem_id}")

    async def update(self, judge_case: JudgeCase) -> JudgeCase:
        """Update judge case"""
        try:
            result = (
                await self.supabase.table("judge_cases")
                .update(
                    {
                        "case_name": judge_case.case_name,
                        "input_data": judge_case.input_data,
                        "expected_output": judge_case.expected_output,
                        "is_public": judge_case.is_public,
                        "time_limit_ms": judge_case.time_limit_ms,
                        "memory_limit_mb": judge_case.memory_limit_mb,
                    }
                )
                .eq("id", str(judge_case.id))
                .execute()
            )

            if result.data:
                return JudgeCase(**result.data[0])
            raise Exception("Failed to update judge case")

        except Exception as e:
            await self._handle_error(e, f"update judge case {judge_case.id}")

    async def delete(self, judge_case_id: UUID) -> bool:
        """Delete judge case"""
        try:
            result = (
                await self.supabase.table("judge_cases")
                .delete()
                .eq("id", str(judge_case_id))
                .execute()
            )
            return len(result.data) > 0 if result.data else False

        except Exception as e:
            await self._handle_error(e, f"delete judge case {judge_case_id}")


# TODO: UserProblemStatusモデルが未実装のため一時コメントアウト
# class SupabaseUserProblemStatusRepository(
#     BaseSupabaseRepository, UserProblemStatusRepositoryInterface
# ):
#     """Supabase implementation of UserProblemStatus repository for Core domain"""
#
#     async def create(self, status: UserProblemStatus) -> UserProblemStatus:
#         """Create a new user problem status"""
#         try:
#             data = {
#                 "user_id": status.user_id,
#                 "problem_id": str(status.problem_id),
#                 "is_solved": status.is_solved,
#                 "score": status.score,
#                 "attempt_count": status.attempt_count,
#                 "solved_at": status.solved_at.isoformat() if status.solved_at else None,
#             }
#
#             # IDが設定されていない場合は生成
#             if status.id:
#                 data["id"] = str(status.id)
#
#             result = (
#                 await self.supabase.table("user_problem_status").insert(data).execute()
#             )
#
#             if result.data:
#                 return UserProblemStatus(**result.data[0])
#             raise Exception("Failed to create user problem status")
#
#         except Exception as e:
#             await self._handle_error(e, "create user problem status")
#
#     async def find_by_user_and_problem(
#         self, user_id: str, problem_id: UUID
#     ) -> Optional[UserProblemStatus]:
#         """Find user problem status by user ID and problem ID"""
#         try:
#             result = await (
#                 self.supabase.table("user_problem_status")
#                 .select("*")
#                 .eq("user_id", user_id)
#                 .eq("problem_id", str(problem_id))
#                 .execute()
#             )
#
#             if result.data:
#                 return UserProblemStatus(**result.data[0])
#             return None
#
#         except Exception as e:
#             await self._handle_error(
#                 e, f"find user problem status for user {user_id} problem {problem_id}"
#             )
#
#     async def find_by_user_id(self, user_id: str) -> List[UserProblemStatus]:
#         """Find all user problem statuses by user ID"""
#         try:
#             result = (
#                 await self.supabase.table("user_problem_status")
#                 .select("*")
#                 .eq("user_id", user_id)
#                 .execute()
#             )
#
#             return (
#                 [UserProblemStatus(**status) for status in result.data]
#                 if result.data
#                 else []
#             )
#
#         except Exception as e:
#             await self._handle_error(e, f"find user problem statuses by user {user_id}")
#
#     async def update(self, status: UserProblemStatus) -> UserProblemStatus:
#         """Update user problem status"""
#         try:
#             result = (
#                 await self.supabase.table("user_problem_status")
#                 .update(
#                     {
#                         "is_solved": status.is_solved,
#                         "score": status.score,
#                         "attempt_count": status.attempt_count,
#                         "solved_at": (
#                             status.solved_at.isoformat() if status.solved_at else None
#                         ),
#                     }
#                 )
#                 .eq("user_id", status.user_id)
#                 .eq("problem_id", str(status.problem_id))
#                 .execute()
#             )
#
#             if result.data:
#                 return UserProblemStatus(**result.data[0])
#             raise Exception("Failed to update user problem status")
#
#         except Exception as e:
#             await self._handle_error(
#                 e, f"update user problem status {status.user_id}/{status.problem_id}"
#             )
#
#     async def delete(self, user_id: str, problem_id: UUID) -> bool:
#         """Delete user problem status"""
#         try:
#             result = await (
#                 self.supabase.table("user_problem_status")
#                 .delete()
#                 .eq("user_id", user_id)
#                 .eq("problem_id", str(problem_id))
#                 .execute()
#             )
#             return len(result.data) > 0 if result.data else False
#
#         except Exception as e:
#             await self._handle_error(
#                 e, f"delete user problem status {user_id}/{problem_id}"
#             )
