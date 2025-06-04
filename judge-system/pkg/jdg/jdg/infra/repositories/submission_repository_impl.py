"""
Submission Repository implementation using Supabase
提出リポジトリのSupabase実装
"""

import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from supabase import Client
from ...domain.repositories.submission_repository import SubmissionRepository
from ...domain.models import Submission, ExecutionResult, JudgeCaseResult
from ....const import (
    ProgrammingLanguage as Language,
    JudgeResultType as JudgeResult,
    ExecutionStatus,
)


logger = logging.getLogger(__name__)


class SubmissionRepositoryImpl(SubmissionRepository):
    """Supabaseを使った提出リポジトリの実装"""

    def __init__(self, supabase_client: Client):
        self.client = supabase_client

    async def save(self, submission: Submission) -> bool:
        """提出を保存"""
        try:
            data = {
                "id": str(submission.id),
                "problem_id": str(submission.problem_id),
                "user_id": str(submission.user_id),
                "code": submission.code,
                "language": submission.language.value,
                "status": submission.status.value,
                "overall_result": submission.overall_result.value,
                "total_points": submission.total_points,
                "max_points": submission.max_points,
                "execution_time": submission.execution_time,
                "memory_usage": submission.memory_usage,
                "submitted_at": submission.submitted_at.isoformat(),
                "judged_at": (
                    submission.judged_at.isoformat() if submission.judged_at else None
                ),
                "metadata": submission.metadata,
            }

            # 既存レコードがあるかチェック
            existing = (
                self.client.table("submissions")
                .select("id")
                .eq("id", str(submission.id))
                .execute()
            )

            if existing.data:
                # 更新
                result = (
                    self.client.table("submissions")
                    .update(data)
                    .eq("id", str(submission.id))
                    .execute()
                )
            else:
                # 新規作成
                result = self.client.table("submissions").insert(data).execute()

            # ジャッジケース結果も保存
            if submission.judge_case_results:
                await self._save_judge_case_results(
                    submission.id, submission.judge_case_results
                )

            logger.info(f"Submission saved successfully: {submission.id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save submission {submission.id}: {e}")
            return False

    async def find_by_id(self, submission_id: uuid.UUID) -> Optional[Submission]:
        """IDで提出を検索"""
        try:
            result = (
                self.client.table("submissions")
                .select("*")
                .eq("id", str(submission_id))
                .execute()
            )

            if not result.data:
                return None

            submission_data = result.data[0]
            submission = self._map_to_submission(submission_data)

            # ジャッジケース結果も取得
            submission.judge_case_results = await self._get_judge_case_results(
                submission_id
            )

            return submission

        except Exception as e:
            logger.error(f"Failed to find submission by id {submission_id}: {e}")
            return None

    async def find_by_user(
        self, user_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> List[Submission]:
        """ユーザーIDで提出を検索"""
        try:
            result = (
                self.client.table("submissions")
                .select("*")
                .eq("user_id", str(user_id))
                .order("submitted_at", desc=True)
                .limit(limit)
                .offset(offset)
                .execute()
            )

            submissions = []
            for data in result.data:
                submission = self._map_to_submission(data)
                submissions.append(submission)

            return submissions

        except Exception as e:
            logger.error(f"Failed to find submissions by user {user_id}: {e}")
            return []

    async def find_by_problem(
        self, problem_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> List[Submission]:
        """問題IDで提出を検索"""
        try:
            result = (
                self.client.table("submissions")
                .select("*")
                .eq("problem_id", str(problem_id))
                .order("submitted_at", desc=True)
                .limit(limit)
                .offset(offset)
                .execute()
            )

            submissions = []
            for data in result.data:
                submission = self._map_to_submission(data)
                submissions.append(submission)

            return submissions

        except Exception as e:
            logger.error(f"Failed to find submissions by problem {problem_id}: {e}")
            return []

    async def find_by_user_and_problem(
        self, user_id: uuid.UUID, problem_id: uuid.UUID
    ) -> List[Submission]:
        """ユーザーと問題で提出を検索"""
        try:
            result = (
                self.client.table("submissions")
                .select("*")
                .eq("user_id", str(user_id))
                .eq("problem_id", str(problem_id))
                .order("submitted_at", desc=True)
                .execute()
            )

            submissions = []
            for data in result.data:
                submission = self._map_to_submission(data)
                submissions.append(submission)

            return submissions

        except Exception as e:
            logger.error(
                f"Failed to find submissions by user {user_id} and problem {problem_id}: {e}"
            )
            return []

    async def find_by_status(
        self, status: ExecutionStatus, limit: int = 50
    ) -> List[Submission]:
        """ステータスで提出を検索"""
        try:
            result = (
                self.client.table("submissions")
                .select("*")
                .eq("status", status.value)
                .order("submitted_at", desc=True)
                .limit(limit)
                .execute()
            )

            submissions = []
            for data in result.data:
                submission = self._map_to_submission(data)
                submissions.append(submission)

            return submissions

        except Exception as e:
            logger.error(f"Failed to find submissions by status {status}: {e}")
            return []

    async def find_by_result(
        self, result: JudgeResult, limit: int = 50
    ) -> List[Submission]:
        """結果で提出を検索"""
        try:
            query_result = (
                self.client.table("submissions")
                .select("*")
                .eq("overall_result", result.value)
                .order("submitted_at", desc=True)
                .limit(limit)
                .execute()
            )

            submissions = []
            for data in query_result.data:
                submission = self._map_to_submission(data)
                submissions.append(submission)

            return submissions

        except Exception as e:
            logger.error(f"Failed to find submissions by result {result}: {e}")
            return []

    async def find_by_language(
        self, language: Language, limit: int = 50
    ) -> List[Submission]:
        """言語で提出を検索"""
        try:
            result = (
                self.client.table("submissions")
                .select("*")
                .eq("language", language.value)
                .order("submitted_at", desc=True)
                .limit(limit)
                .execute()
            )

            submissions = []
            for data in result.data:
                submission = self._map_to_submission(data)
                submissions.append(submission)

            return submissions

        except Exception as e:
            logger.error(f"Failed to find submissions by language {language}: {e}")
            return []

    async def find_recent(self, limit: int = 50) -> List[Submission]:
        """最近の提出を検索"""
        try:
            result = (
                self.client.table("submissions")
                .select("*")
                .order("submitted_at", desc=True)
                .limit(limit)
                .execute()
            )

            submissions = []
            for data in result.data:
                submission = self._map_to_submission(data)
                submissions.append(submission)

            return submissions

        except Exception as e:
            logger.error(f"Failed to find recent submissions: {e}")
            return []

    async def find_user_best_submissions(
        self, user_id: uuid.UUID, problem_ids: List[uuid.UUID]
    ) -> List[Submission]:
        """ユーザーの最高得点提出を取得"""
        try:
            problem_id_strs = [str(pid) for pid in problem_ids]

            # 各問題について最高得点の提出を取得
            best_submissions = []

            for problem_id_str in problem_id_strs:
                result = (
                    self.client.table("submissions")
                    .select("*")
                    .eq("user_id", str(user_id))
                    .eq("problem_id", problem_id_str)
                    .order("total_points", desc=True)
                    .order("submitted_at", desc=True)
                    .limit(1)
                    .execute()
                )

                if result.data:
                    submission = self._map_to_submission(result.data[0])
                    best_submissions.append(submission)

            return best_submissions

        except Exception as e:
            logger.error(
                f"Failed to find user best submissions for user {user_id}: {e}"
            )
            return []

    async def count_by_user(self, user_id: uuid.UUID) -> int:
        """ユーザーの提出数をカウント"""
        try:
            result = (
                self.client.table("submissions")
                .select("id", count="exact")
                .eq("user_id", str(user_id))
                .execute()
            )

            return result.count or 0

        except Exception as e:
            logger.error(f"Failed to count submissions by user {user_id}: {e}")
            return 0

    async def count_by_problem(self, problem_id: uuid.UUID) -> int:
        """問題の提出数をカウント"""
        try:
            result = (
                self.client.table("submissions")
                .select("id", count="exact")
                .eq("problem_id", str(problem_id))
                .execute()
            )

            return result.count or 0

        except Exception as e:
            logger.error(f"Failed to count submissions by problem {problem_id}: {e}")
            return 0

    async def count_by_result(self, result: JudgeResult) -> int:
        """結果別の提出数をカウント"""
        try:
            query_result = (
                self.client.table("submissions")
                .select("id", count="exact")
                .eq("overall_result", result.value)
                .execute()
            )

            return query_result.count or 0

        except Exception as e:
            logger.error(f"Failed to count submissions by result {result}: {e}")
            return 0

    async def get_user_statistics(self, user_id: uuid.UUID) -> dict:
        """ユーザーの統計情報を取得"""
        try:
            # 提出数を取得
            total_count = await self.count_by_user(user_id)

            # 結果別の統計を取得
            stats = {"total_submissions": total_count}

            for result in JudgeResult:
                result_count = (
                    self.client.table("submissions")
                    .select("id", count="exact")
                    .eq("user_id", str(user_id))
                    .eq("overall_result", result.value)
                    .execute()
                )
                stats[f"{result.value.lower()}_count"] = result_count.count or 0

            # 言語別統計
            language_stats = {}
            for language in Language:
                lang_count = (
                    self.client.table("submissions")
                    .select("id", count="exact")
                    .eq("user_id", str(user_id))
                    .eq("language", language.value)
                    .execute()
                )
                language_stats[language.value] = lang_count.count or 0

            stats["language_breakdown"] = language_stats

            # 平均実行時間と最高得点
            result = (
                self.client.table("submissions")
                .select("execution_time, total_points")
                .eq("user_id", str(user_id))
                .execute()
            )

            if result.data:
                execution_times = [
                    data.get("execution_time", 0)
                    for data in result.data
                    if data.get("execution_time")
                ]
                points = [data.get("total_points", 0) for data in result.data]

                stats["avg_execution_time"] = (
                    sum(execution_times) / len(execution_times)
                    if execution_times
                    else 0
                )
                stats["max_points"] = max(points) if points else 0

            return stats

        except Exception as e:
            logger.error(f"Failed to get user statistics for {user_id}: {e}")
            return {}

    async def get_problem_statistics(self, problem_id: uuid.UUID) -> dict:
        """問題の統計情報を取得"""
        try:
            # 提出数を取得
            total_count = await self.count_by_problem(problem_id)

            # 結果別の統計を取得
            stats = {"total_submissions": total_count}

            for result in JudgeResult:
                result_count = (
                    self.client.table("submissions")
                    .select("id", count="exact")
                    .eq("problem_id", str(problem_id))
                    .eq("overall_result", result.value)
                    .execute()
                )
                stats[f"{result.value.lower()}_count"] = result_count.count or 0

            # AC率を計算
            ac_count = stats.get("ac_count", 0)
            stats["acceptance_rate"] = (
                (ac_count / total_count * 100) if total_count > 0 else 0
            )

            # 言語別統計
            language_stats = {}
            for language in Language:
                lang_count = (
                    self.client.table("submissions")
                    .select("id", count="exact")
                    .eq("problem_id", str(problem_id))
                    .eq("language", language.value)
                    .execute()
                )
                language_stats[language.value] = lang_count.count or 0

            stats["language_breakdown"] = language_stats

            # ユニークユーザー数
            unique_users = (
                self.client.table("submissions")
                .select("user_id")
                .eq("problem_id", str(problem_id))
                .execute()
            )

            unique_user_ids = set(data["user_id"] for data in unique_users.data)
            stats["unique_users"] = len(unique_user_ids)

            return stats

        except Exception as e:
            logger.error(f"Failed to get problem statistics for {problem_id}: {e}")
            return {}

    async def delete(self, submission_id: uuid.UUID) -> bool:
        """提出を削除"""
        try:
            # ジャッジケース結果も削除
            self.client.table("judge_case_results").delete().eq(
                "submission_id", str(submission_id)
            ).execute()

            # 提出を削除
            result = (
                self.client.table("submissions")
                .delete()
                .eq("id", str(submission_id))
                .execute()
            )

            logger.info(f"Submission deleted successfully: {submission_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete submission {submission_id}: {e}")
            return False

    def _map_to_submission(self, data: Dict[str, Any]) -> Submission:
        """データベースレコードをSubmissionオブジェクトにマップ"""
        return Submission(
            id=uuid.UUID(data["id"]),
            problem_id=uuid.UUID(data["problem_id"]),
            user_id=uuid.UUID(data["user_id"]),
            code=data["code"],
            language=Language(data["language"]),
            status=ExecutionStatus(data["status"]),
            overall_result=JudgeResult(data["overall_result"]),
            total_points=data.get("total_points", 0),
            max_points=data.get("max_points", 0),
            execution_time=data.get("execution_time", 0.0),
            memory_usage=data.get("memory_usage", 0),
            submitted_at=datetime.fromisoformat(data["submitted_at"]),
            judged_at=(
                datetime.fromisoformat(data["judged_at"])
                if data.get("judged_at")
                else None
            ),
            metadata=data.get("metadata", {}),
        )

    async def _save_judge_case_results(
        self, submission_id: uuid.UUID, results: List[JudgeCaseResult]
    ) -> None:
        """ジャッジケース結果を保存"""
        try:
            # 既存の結果を削除
            self.client.table("judge_case_results").delete().eq(
                "submission_id", str(submission_id)
            ).execute()

            # 新しい結果を保存
            for result in results:
                data = {
                    "submission_id": str(submission_id),
                    "judge_case_id": str(result.judge_case_id),
                    "result": result.result.value,
                    "points": result.points,
                    "feedback": result.feedback,
                    "execution_status": result.execution_result.status.value,
                    "execution_output": result.execution_result.output,
                    "execution_error": result.execution_result.error,
                    "execution_time": result.execution_result.execution_time,
                    "memory_usage": result.execution_result.memory_usage,
                    "exit_code": result.execution_result.exit_code,
                    "stdout": result.execution_result.stdout,
                    "stderr": result.execution_result.stderr,
                    "created_at": result.created_at.isoformat(),
                }

                self.client.table("judge_case_results").insert(data).execute()

        except Exception as e:
            logger.error(
                f"Failed to save judge case results for submission {submission_id}: {e}"
            )

    async def _get_judge_case_results(
        self, submission_id: uuid.UUID
    ) -> List[JudgeCaseResult]:
        """ジャッジケース結果を取得"""
        try:
            result = (
                self.client.table("judge_case_results")
                .select("*")
                .eq("submission_id", str(submission_id))
                .order("created_at")
                .execute()
            )

            judge_case_results = []
            for data in result.data:
                execution_result = ExecutionResult(
                    status=ExecutionStatus(data["execution_status"]),
                    output=data.get("execution_output", ""),
                    error=data.get("execution_error", ""),
                    execution_time=data.get("execution_time", 0.0),
                    memory_usage=data.get("memory_usage", 0),
                    exit_code=data.get("exit_code", 0),
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                )

                judge_case_result = JudgeCaseResult(
                    judge_case_id=uuid.UUID(data["judge_case_id"]),
                    result=JudgeResult(data["result"]),
                    execution_result=execution_result,
                    points=data.get("points", 0),
                    feedback=data.get("feedback", ""),
                    created_at=datetime.fromisoformat(data["created_at"]),
                )

                judge_case_results.append(judge_case_result)

            return judge_case_results

        except Exception as e:
            logger.error(
                f"Failed to get judge case results for submission {submission_id}: {e}"
            )
            return []
