"""
Supabase-based repository implementations for Judge domain
Author: Judge System Team
Date: 2025-01-12
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID
import logging
from datetime import datetime

import asyncpg
from supabase import AsyncClient

from src.domain.models import (
    Problem,
    JudgeCase,
    Submission,
    JudgeProcess,
    JudgeCaseResult,
    JudgeCaseResultMetadata,
    UserProblemStatus,
    Book,
    CaseFile,
)


logger = logging.getLogger(__name__)


class BaseSupabaseRepository(ABC):
    """Base class for Supabase repositories"""

    def __init__(self, supabase_client: AsyncClient):
        self.supabase = supabase_client

    async def _handle_error(self, error: Exception, operation: str) -> None:
        """Handle repository errors with logging"""
        logger.error(f"Repository error in {operation}: {str(error)}")
        raise


class BookRepositoryInterface(ABC):
    """Abstract interface for Book repository"""

    @abstractmethod
    async def create(self, book: Book) -> Book:
        pass

    @abstractmethod
    async def get_by_id(self, book_id: UUID) -> Optional[Book]:
        pass

    @abstractmethod
    async def get_published(self) -> List[Book]:
        pass

    @abstractmethod
    async def update(self, book: Book) -> Book:
        pass

    @abstractmethod
    async def delete(self, book_id: UUID) -> bool:
        pass


class ProblemRepositoryInterface(ABC):
    """Abstract interface for Problem repository"""

    @abstractmethod
    async def create(self, problem: Problem) -> Problem:
        pass

    @abstractmethod
    async def get_by_id(self, problem_id: UUID) -> Optional[Problem]:
        pass

    @abstractmethod
    async def get_by_book_id(self, book_id: UUID) -> List[Problem]:
        pass

    @abstractmethod
    async def get_published(self) -> List[Problem]:
        pass

    @abstractmethod
    async def update(self, problem: Problem) -> Problem:
        pass

    @abstractmethod
    async def delete(self, problem_id: UUID) -> bool:
        pass


class JudgeCaseRepositoryInterface(ABC):
    """Abstract interface for JudgeCase repository"""

    @abstractmethod
    async def create(self, judge_case: JudgeCase) -> JudgeCase:
        pass

    @abstractmethod
    async def get_by_id(self, judge_case_id: UUID) -> Optional[JudgeCase]:
        pass

    @abstractmethod
    async def get_by_problem_id(self, problem_id: UUID) -> List[JudgeCase]:
        pass

    @abstractmethod
    async def update(self, judge_case: JudgeCase) -> JudgeCase:
        pass

    @abstractmethod
    async def delete(self, judge_case_id: UUID) -> bool:
        pass


class SubmissionRepositoryInterface(ABC):
    """Abstract interface for Submission repository"""

    @abstractmethod
    async def create(self, submission: Submission) -> Submission:
        pass

    @abstractmethod
    async def get_by_id(self, submission_id: UUID) -> Optional[Submission]:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID, limit: int = 10) -> List[Submission]:
        pass

    @abstractmethod
    async def get_by_problem_id(
        self, problem_id: UUID, limit: int = 10
    ) -> List[Submission]:
        pass

    @abstractmethod
    async def get_by_user_and_problem(
        self, user_id: UUID, problem_id: UUID, limit: int = 10
    ) -> List[Submission]:
        pass

    @abstractmethod
    async def update(self, submission: Submission) -> Submission:
        pass

    @abstractmethod
    async def delete(self, submission_id: UUID) -> bool:
        pass


class JudgeProcessRepositoryInterface(ABC):
    """Abstract interface for JudgeProcess repository"""

    @abstractmethod
    async def create(self, judge_process: JudgeProcess) -> JudgeProcess:
        pass

    @abstractmethod
    async def get_by_id(self, judge_process_id: UUID) -> Optional[JudgeProcess]:
        pass

    @abstractmethod
    async def get_by_submission_id(self, submission_id: UUID) -> List[JudgeProcess]:
        pass

    @abstractmethod
    async def update(self, judge_process: JudgeProcess) -> JudgeProcess:
        pass

    @abstractmethod
    async def delete(self, judge_process_id: UUID) -> bool:
        pass


class JudgeCaseResultRepositoryInterface(ABC):
    """Abstract interface for JudgeCaseResult repository"""

    @abstractmethod
    async def create(self, judge_case_result: JudgeCaseResult) -> JudgeCaseResult:
        pass

    @abstractmethod
    async def get_by_id(self, result_id: UUID) -> Optional[JudgeCaseResult]:
        pass

    @abstractmethod
    async def get_by_judge_process_id(
        self, judge_process_id: UUID
    ) -> List[JudgeCaseResult]:
        pass

    @abstractmethod
    async def update(self, judge_case_result: JudgeCaseResult) -> JudgeCaseResult:
        pass

    @abstractmethod
    async def delete(self, result_id: UUID) -> bool:
        pass


class UserProblemStatusRepositoryInterface(ABC):
    """Abstract interface for UserProblemStatus repository"""

    @abstractmethod
    async def create(self, status: UserProblemStatus) -> UserProblemStatus:
        pass

    @abstractmethod
    async def get_by_user_and_problem(
        self, user_id: UUID, problem_id: UUID
    ) -> Optional[UserProblemStatus]:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> List[UserProblemStatus]:
        pass

    @abstractmethod
    async def update(self, status: UserProblemStatus) -> UserProblemStatus:
        pass

    @abstractmethod
    async def upsert(self, status: UserProblemStatus) -> UserProblemStatus:
        pass


# =====================================================
# Supabase Repository Implementations
# =====================================================


class SupabaseBookRepository(BaseSupabaseRepository, BookRepositoryInterface):
    """Supabase implementation of Book repository"""

    async def create(self, book: Book) -> Book:
        try:
            result = (
                await self.supabase.table("books")
                .insert(
                    {
                        "title": book.title,
                        "author": book.author,
                        "published_date": book.published_date.isoformat(),
                        "is_published": book.is_published,
                    }
                )
                .execute()
            )

            if result.data:
                return Book(**result.data[0])
            raise Exception("Failed to create book")

        except Exception as e:
            await self._handle_error(e, "create book")

    async def get_by_id(self, book_id: UUID) -> Optional[Book]:
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
            await self._handle_error(e, f"get book {book_id}")

    async def get_published(self) -> List[Book]:
        try:
            result = (
                await self.supabase.table("books")
                .select("*")
                .eq("is_published", True)
                .execute()
            )

            return [Book(**book) for book in result.data] if result.data else []

        except Exception as e:
            await self._handle_error(e, "get published books")

    async def update(self, book: Book) -> Book:
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
    """Supabase implementation of Problem repository"""

    async def create(self, problem: Problem) -> Problem:
        try:
            result = (
                await self.supabase.table("problems")
                .insert(
                    {
                        "title": problem.title,
                        "description": problem.description,
                        "book_id": str(problem.book_id) if problem.book_id else None,
                        "difficulty_level": problem.difficulty_level,
                        "status": problem.status,
                    }
                )
                .execute()
            )

            if result.data:
                return Problem(**result.data[0])
            raise Exception("Failed to create problem")

        except Exception as e:
            await self._handle_error(e, "create problem")

    async def get_by_id(self, problem_id: UUID) -> Optional[Problem]:
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
            await self._handle_error(e, f"get problem {problem_id}")

    async def get_by_book_id(self, book_id: UUID) -> List[Problem]:
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
            await self._handle_error(e, f"get problems by book {book_id}")

    async def get_published(self) -> List[Problem]:
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
            await self._handle_error(e, "get published problems")

    async def update(self, problem: Problem) -> Problem:
        try:
            result = (
                await self.supabase.table("problems")
                .update(
                    {
                        "title": problem.title,
                        "description": problem.description,
                        "book_id": str(problem.book_id) if problem.book_id else None,
                        "difficulty_level": problem.difficulty_level,
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
    """Supabase implementation of JudgeCase repository"""

    async def create(self, judge_case: JudgeCase) -> JudgeCase:
        try:
            result = (
                await self.supabase.table("judge_cases")
                .insert(
                    {
                        "problem_id": str(judge_case.problem_id),
                        "input_id": str(judge_case.input_id),
                        "output_id": str(judge_case.output_id),
                        "is_sample": judge_case.is_sample,
                        "display_order": judge_case.display_order,
                    }
                )
                .execute()
            )

            if result.data:
                return JudgeCase(**result.data[0])
            raise Exception("Failed to create judge case")

        except Exception as e:
            await self._handle_error(e, "create judge case")

    async def get_by_id(self, judge_case_id: UUID) -> Optional[JudgeCase]:
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
            await self._handle_error(e, f"get judge case {judge_case_id}")

    async def get_by_problem_id(self, problem_id: UUID) -> List[JudgeCase]:
        try:
            result = (
                await self.supabase.table("judge_cases")
                .select("*")
                .eq("problem_id", str(problem_id))
                .order("display_order")
                .execute()
            )

            return [JudgeCase(**case) for case in result.data] if result.data else []

        except Exception as e:
            await self._handle_error(e, f"get judge cases by problem {problem_id}")

    async def update(self, judge_case: JudgeCase) -> JudgeCase:
        try:
            result = (
                await self.supabase.table("judge_cases")
                .update(
                    {
                        "problem_id": str(judge_case.problem_id),
                        "input_id": str(judge_case.input_id),
                        "output_id": str(judge_case.output_id),
                        "is_sample": judge_case.is_sample,
                        "display_order": judge_case.display_order,
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


class SupabaseSubmissionRepository(
    BaseSupabaseRepository, SubmissionRepositoryInterface
):
    """Supabase implementation of Submission repository"""

    async def create(self, submission: Submission) -> Submission:
        try:
            result = (
                await self.supabase.table("submissions")
                .insert(
                    {
                        "problem_id": str(submission.problem_id),
                        "user_id": str(submission.user_id),
                        "code": submission.code,
                        "language": submission.language,
                        "status": submission.status,
                        "score": submission.score,
                    }
                )
                .execute()
            )

            if result.data:
                return Submission(**result.data[0])
            raise Exception("Failed to create submission")

        except Exception as e:
            await self._handle_error(e, "create submission")

    async def get_by_id(self, submission_id: UUID) -> Optional[Submission]:
        try:
            result = (
                await self.supabase.table("submissions")
                .select("*")
                .eq("id", str(submission_id))
                .execute()
            )

            if result.data:
                return Submission(**result.data[0])
            return None

        except Exception as e:
            await self._handle_error(e, f"get submission {submission_id}")

    async def get_by_user_id(self, user_id: UUID, limit: int = 10) -> List[Submission]:
        try:
            result = (
                await self.supabase.table("submissions")
                .select("*")
                .eq("user_id", str(user_id))
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            return (
                [Submission(**submission) for submission in result.data]
                if result.data
                else []
            )

        except Exception as e:
            await self._handle_error(e, f"get submissions by user {user_id}")

    async def get_by_problem_id(
        self, problem_id: UUID, limit: int = 10
    ) -> List[Submission]:
        try:
            result = (
                await self.supabase.table("submissions")
                .select("*")
                .eq("problem_id", str(problem_id))
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            return (
                [Submission(**submission) for submission in result.data]
                if result.data
                else []
            )

        except Exception as e:
            await self._handle_error(e, f"get submissions by problem {problem_id}")

    async def get_by_user_and_problem(
        self, user_id: UUID, problem_id: UUID, limit: int = 10
    ) -> List[Submission]:
        try:
            result = await (
                self.supabase.table("submissions")
                .select("*")
                .eq("user_id", str(user_id))
                .eq("problem_id", str(problem_id))
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            return (
                [Submission(**submission) for submission in result.data]
                if result.data
                else []
            )

        except Exception as e:
            await self._handle_error(
                e, f"get submissions by user {user_id} and problem {problem_id}"
            )

    async def update(self, submission: Submission) -> Submission:
        try:
            result = (
                await self.supabase.table("submissions")
                .update({"status": submission.status, "score": submission.score})
                .eq("id", str(submission.id))
                .execute()
            )

            if result.data:
                return Submission(**result.data[0])
            raise Exception("Failed to update submission")

        except Exception as e:
            await self._handle_error(e, f"update submission {submission.id}")

    async def delete(self, submission_id: UUID) -> bool:
        try:
            result = (
                await self.supabase.table("submissions")
                .delete()
                .eq("id", str(submission_id))
                .execute()
            )
            return len(result.data) > 0 if result.data else False

        except Exception as e:
            await self._handle_error(e, f"delete submission {submission_id}")


class SupabaseJudgeProcessRepository(
    BaseSupabaseRepository, JudgeProcessRepositoryInterface
):
    """Supabase implementation of JudgeProcess repository"""

    async def create(self, judge_process: JudgeProcess) -> JudgeProcess:
        try:
            result = (
                await self.supabase.table("judge_processes")
                .insert(
                    {
                        "submission_id": str(judge_process.submission_id),
                        "status": judge_process.status.value,
                        "result": judge_process.result,
                        "execution_time_ms": judge_process.execution_time_ms,
                        "memory_usage_kb": judge_process.memory_usage_kb,
                    }
                )
                .execute()
            )

            if result.data:
                return JudgeProcess(**result.data[0])
            raise Exception("Failed to create judge process")

        except Exception as e:
            await self._handle_error(e, "create judge process")

    async def get_by_id(self, judge_process_id: UUID) -> Optional[JudgeProcess]:
        try:
            result = (
                await self.supabase.table("judge_processes")
                .select("*")
                .eq("id", str(judge_process_id))
                .execute()
            )

            if result.data:
                return JudgeProcess(**result.data[0])
            return None

        except Exception as e:
            await self._handle_error(e, f"get judge process {judge_process_id}")

    async def get_by_submission_id(self, submission_id: UUID) -> List[JudgeProcess]:
        try:
            result = (
                await self.supabase.table("judge_processes")
                .select("*")
                .eq("submission_id", str(submission_id))
                .order("created_at", desc=True)
                .execute()
            )

            return (
                [JudgeProcess(**process) for process in result.data]
                if result.data
                else []
            )

        except Exception as e:
            await self._handle_error(
                e, f"get judge processes by submission {submission_id}"
            )

    async def update(self, judge_process: JudgeProcess) -> JudgeProcess:
        try:
            result = (
                await self.supabase.table("judge_processes")
                .update(
                    {
                        "status": judge_process.status.value,
                        "result": judge_process.result,
                        "execution_time_ms": judge_process.execution_time_ms,
                        "memory_usage_kb": judge_process.memory_usage_kb,
                    }
                )
                .eq("id", str(judge_process.id))
                .execute()
            )

            if result.data:
                return JudgeProcess(**result.data[0])
            raise Exception("Failed to update judge process")

        except Exception as e:
            await self._handle_error(e, f"update judge process {judge_process.id}")

    async def delete(self, judge_process_id: UUID) -> bool:
        try:
            result = (
                await self.supabase.table("judge_processes")
                .delete()
                .eq("id", str(judge_process_id))
                .execute()
            )
            return len(result.data) > 0 if result.data else False

        except Exception as e:
            await self._handle_error(e, f"delete judge process {judge_process_id}")


class SupabaseJudgeCaseResultRepository(
    BaseSupabaseRepository, JudgeCaseResultRepositoryInterface
):
    """Supabase implementation of JudgeCaseResult repository"""

    async def create(self, judge_case_result: JudgeCaseResult) -> JudgeCaseResult:
        try:
            result = (
                await self.supabase.table("judge_case_results")
                .insert(
                    {
                        "judge_process_id": str(judge_case_result.judge_process_id),
                        "judge_case_id": str(judge_case_result.judge_case_id),
                        "status": judge_case_result.status,
                        "result": judge_case_result.result,
                        "error": judge_case_result.error,
                        "warning": judge_case_result.warning,
                        "processing_time_ms": judge_case_result.processing_time_ms,
                        "memory_usage_kb": judge_case_result.memory_usage_kb,
                    }
                )
                .execute()
            )

            if result.data:
                case_result = JudgeCaseResult(**result.data[0])

                # Create metadata if provided
                if judge_case_result.metadata:
                    await self._create_metadata(
                        case_result.id, judge_case_result.metadata
                    )

                return case_result
            raise Exception("Failed to create judge case result")

        except Exception as e:
            await self._handle_error(e, "create judge case result")

    async def _create_metadata(
        self, result_id: UUID, metadata: JudgeCaseResultMetadata
    ) -> None:
        """Create metadata for judge case result"""
        await self.supabase.table("judge_case_result_metadata").insert(
            {
                "judge_case_result_id": str(result_id),
                "memory_used_kb": metadata.memory_used_kb,
                "time_used_ms": metadata.time_used_ms,
                "compile_error": metadata.compile_error,
                "runtime_error": metadata.runtime_error,
                "output": metadata.output,
            }
        ).execute()

    async def get_by_id(self, result_id: UUID) -> Optional[JudgeCaseResult]:
        try:
            # Get result with metadata
            result = await (
                self.supabase.table("judge_case_results")
                .select("*, judge_case_result_metadata(*)")
                .eq("id", str(result_id))
                .execute()
            )

            if result.data:
                data = result.data[0]
                metadata = None
                if data.get("judge_case_result_metadata"):
                    metadata = JudgeCaseResultMetadata(
                        **data["judge_case_result_metadata"][0]
                    )

                # Remove metadata from main data to avoid conflicts
                data.pop("judge_case_result_metadata", None)

                case_result = JudgeCaseResult(**data)
                case_result.metadata = metadata
                return case_result
            return None

        except Exception as e:
            await self._handle_error(e, f"get judge case result {result_id}")

    async def get_by_judge_process_id(
        self, judge_process_id: UUID
    ) -> List[JudgeCaseResult]:
        try:
            result = await (
                self.supabase.table("judge_case_results")
                .select("*, judge_case_result_metadata(*)")
                .eq("judge_process_id", str(judge_process_id))
                .execute()
            )

            results = []
            if result.data:
                for data in result.data:
                    metadata = None
                    if data.get("judge_case_result_metadata"):
                        metadata = JudgeCaseResultMetadata(
                            **data["judge_case_result_metadata"][0]
                        )

                    # Remove metadata from main data
                    data.pop("judge_case_result_metadata", None)

                    case_result = JudgeCaseResult(**data)
                    case_result.metadata = metadata
                    results.append(case_result)

            return results

        except Exception as e:
            await self._handle_error(
                e, f"get judge case results by process {judge_process_id}"
            )

    async def update(self, judge_case_result: JudgeCaseResult) -> JudgeCaseResult:
        try:
            result = (
                await self.supabase.table("judge_case_results")
                .update(
                    {
                        "status": judge_case_result.status,
                        "result": judge_case_result.result,
                        "error": judge_case_result.error,
                        "warning": judge_case_result.warning,
                        "processing_time_ms": judge_case_result.processing_time_ms,
                        "memory_usage_kb": judge_case_result.memory_usage_kb,
                    }
                )
                .eq("id", str(judge_case_result.id))
                .execute()
            )

            if result.data:
                # Update metadata if provided
                if judge_case_result.metadata:
                    await self._update_metadata(
                        judge_case_result.id, judge_case_result.metadata
                    )

                return JudgeCaseResult(**result.data[0])
            raise Exception("Failed to update judge case result")

        except Exception as e:
            await self._handle_error(
                e, f"update judge case result {judge_case_result.id}"
            )

    async def _update_metadata(
        self, result_id: UUID, metadata: JudgeCaseResultMetadata
    ) -> None:
        """Update metadata for judge case result"""
        await self.supabase.table("judge_case_result_metadata").upsert(
            {
                "judge_case_result_id": str(result_id),
                "memory_used_kb": metadata.memory_used_kb,
                "time_used_ms": metadata.time_used_ms,
                "compile_error": metadata.compile_error,
                "runtime_error": metadata.runtime_error,
                "output": metadata.output,
            }
        ).execute()

    async def delete(self, result_id: UUID) -> bool:
        try:
            result = (
                await self.supabase.table("judge_case_results")
                .delete()
                .eq("id", str(result_id))
                .execute()
            )
            return len(result.data) > 0 if result.data else False

        except Exception as e:
            await self._handle_error(e, f"delete judge case result {result_id}")


class SupabaseUserProblemStatusRepository(
    BaseSupabaseRepository, UserProblemStatusRepositoryInterface
):
    """Supabase implementation of UserProblemStatus repository"""

    async def create(self, status: UserProblemStatus) -> UserProblemStatus:
        try:
            result = (
                await self.supabase.table("user_problem_status")
                .insert(
                    {
                        "user_id": status.user_id,
                        "problem_id": status.problem_id,
                        "solved": status.solved,
                        "solved_at": (
                            status.solved_at.isoformat() if status.solved_at else None
                        ),
                        "submission_count": status.submission_count,
                        "last_submission_id": status.last_submission_id,
                        "best_score": status.best_score,
                    }
                )
                .execute()
            )

            if result.data:
                return UserProblemStatus(**result.data[0])
            raise Exception("Failed to create user problem status")

        except Exception as e:
            await self._handle_error(e, "create user problem status")

    async def get_by_user_and_problem(
        self, user_id: UUID, problem_id: UUID
    ) -> Optional[UserProblemStatus]:
        try:
            result = await (
                self.supabase.table("user_problem_status")
                .select("*")
                .eq("user_id", str(user_id))
                .eq("problem_id", str(problem_id))
                .execute()
            )

            if result.data:
                return UserProblemStatus(**result.data[0])
            return None

        except Exception as e:
            await self._handle_error(
                e, f"get user problem status for user {user_id} problem {problem_id}"
            )

    async def get_by_user_id(self, user_id: UUID) -> List[UserProblemStatus]:
        try:
            result = (
                await self.supabase.table("user_problem_status")
                .select("*")
                .eq("user_id", str(user_id))
                .execute()
            )

            return (
                [UserProblemStatus(**status) for status in result.data]
                if result.data
                else []
            )

        except Exception as e:
            await self._handle_error(e, f"get user problem status by user {user_id}")

    async def update(self, status: UserProblemStatus) -> UserProblemStatus:
        try:
            result = (
                await self.supabase.table("user_problem_status")
                .update(
                    {
                        "solved": status.solved,
                        "solved_at": (
                            status.solved_at.isoformat() if status.solved_at else None
                        ),
                        "submission_count": status.submission_count,
                        "last_submission_id": status.last_submission_id,
                        "best_score": status.best_score,
                    }
                )
                .eq("user_id", status.user_id)
                .eq("problem_id", status.problem_id)
                .execute()
            )

            if result.data:
                return UserProblemStatus(**result.data[0])
            raise Exception("Failed to update user problem status")

        except Exception as e:
            await self._handle_error(
                e, f"update user problem status {status.user_id}/{status.problem_id}"
            )

    async def upsert(self, status: UserProblemStatus) -> UserProblemStatus:
        try:
            result = (
                await self.supabase.table("user_problem_status")
                .upsert(
                    {
                        "user_id": status.user_id,
                        "problem_id": status.problem_id,
                        "solved": status.solved,
                        "solved_at": (
                            status.solved_at.isoformat() if status.solved_at else None
                        ),
                        "submission_count": status.submission_count,
                        "last_submission_id": status.last_submission_id,
                        "best_score": status.best_score,
                    }
                )
                .execute()
            )

            if result.data:
                return UserProblemStatus(**result.data[0])
            raise Exception("Failed to upsert user problem status")

        except Exception as e:
            await self._handle_error(
                e, f"upsert user problem status {status.user_id}/{status.problem_id}"
            )
