"""
API Submission Use Cases
API提出ユースケース

APIリクエストから呼び出される提出関連のワークフローを実装
"""

import uuid
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from dependency_injector.wiring import Provide, inject

from ..domain.models import Submission, JudgeQueue
from ..domain.repositories.submission_repository import SubmissionRepositoryBase as SubmissionRepository
from ..domain.repositories.judge_queue_repository import JudgeQueueRepositoryBase as JudgeQueueRepository
from ..domain.services.judge_service import JudgeDomainService
# from ppcore.domain.repositories.problem_repository import ProblemRepository
# from ppcore.domain.repositories.user_repository import UserRepository
from ..domain.entities.enums import (
    ProgrammingLanguage as Language,
    JudgeResultType as JudgeResult,
    ExecutionStatus,
)
# from ppcore.shared.events import EventBus, SubmissionCreatedEvent
from src.utils import get_logger

from ..app.container import JudgeContainer

logger = get_logger(__name__)


class ApiSubmissionUseCase:
    """API提出関連のユースケース（APIワークフロー専用）"""

    @inject
    def __init__(
        self,
        submission_repo: SubmissionRepository = Provide[JudgeContainer.submission_repository],
        queue_repo: JudgeQueueRepository = Provide[JudgeContainer.judge_queue_repository],
        problem_repo: ProblemRepository = Provide[JudgeContainer.problem_repository],
        user_repo: UserRepository = Provide[JudgeContainer.user_repository],
        judge_service: JudgeDomainService = Provide[JudgeContainer.judge_service],
        event_bus: EventBus = Provide[JudgeContainer.event_bus_instance],
    ):
        self.submission_repo = submission_repo
        self.queue_repo = queue_repo
        self.problem_repo = problem_repo
        self.user_repo = user_repo
        self.judge_service = judge_service
        self.event_bus = event_bus

    async def submit_solution(
        self,
        user_id: uuid.UUID,
        problem_id: uuid.UUID,
        code: str,
        language: Language,
        contest_id: Optional[uuid.UUID] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """解答を提出する（API用）"""
        try:
            # バリデーション
            validation_result = await self._validate_submission_request(
                user_id, problem_id, code, language, contest_id
            )
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"],
                    "error_code": validation_result["error_code"],
                }

            # 提出を作成
            submission = await self._create_submission(
                user_id, problem_id, code, language, contest_id, metadata
            )

            if not submission:
                return {
                    "success": False,
                    "error": "Failed to create submission",
                    "error_code": "SUBMISSION_CREATION_FAILED",
                }

            # ジャッジキューに追加
            queue_success = await self._enqueue_submission(submission, contest_id)
            if not queue_success:
                logger.warning(f"Failed to enqueue submission {submission.id}, but submission was created")

            # イベント発行
            await self._publish_submission_created_event(submission, contest_id)

            # レスポンス作成
            return {
                "success": True,
                "submission": {
                    "submission_id": str(submission.id),
                    "status": submission.status.value,
                    "language": submission.language.value,
                    "created_at": submission.submitted_at.isoformat(),
                    "queue_position": await self._get_estimated_queue_position(submission.id),
                },
            }

        except Exception as e:
            logger.error(f"Failed to submit solution: {e}")
            return {
                "success": False,
                "error": "Internal server error",
                "error_code": "INTERNAL_ERROR",
            }

    async def get_submission_status(self, submission_id: uuid.UUID) -> Dict[str, Any]:
        """提出状況を取得（API用）"""
        try:
            submission = await self.submission_repo.find_by_id(submission_id)
            if not submission:
                return {
                    "success": False,
                    "error": "Submission not found",
                    "error_code": "SUBMISSION_NOT_FOUND",
                }

            # キュー状況も取得
            queue_item = await self.queue_repo.find_by_submission(submission_id)
            queue_info = {}
            if queue_item:
                queue_info = {
                    "queue_status": queue_item.status.value,
                    "worker_id": queue_item.worker_id,
                    "started_at": queue_item.started_at.isoformat() if queue_item.started_at else None,
                    "estimated_position": await self._get_estimated_queue_position(submission_id),
                }

            return {
                "success": True,
                "submission": {
                    "submission_id": str(submission.id),
                    "status": submission.status.value,
                    "result": submission.overall_result.value if submission.overall_result else None,
                    "score": submission.total_points,
                    "max_score": submission.max_points,
                    "language": submission.language.value,
                    "created_at": submission.submitted_at.isoformat(),
                    "judged_at": submission.judged_at.isoformat() if submission.judged_at else None,
                    "execution_time_ms": getattr(submission, 'execution_time_ms', None),
                    "memory_usage_mb": getattr(submission, 'memory_usage_mb', None),
                    "judge_case_results": submission.judge_case_results,
                    "queue": queue_info,
                },
            }

        except Exception as e:
            logger.error(f"Failed to get submission status: {e}")
            return {
                "success": False,
                "error": "Internal server error",
                "error_code": "INTERNAL_ERROR",
            }

    async def get_user_submissions(
        self,
        user_id: uuid.UUID,
        problem_id: Optional[uuid.UUID] = None,
        contest_id: Optional[uuid.UUID] = None,
        limit: int = 20,
        offset: int = 0,
        include_code: bool = False,
    ) -> Dict[str, Any]:
        """ユーザーの提出一覧を取得（API用）"""
        try:
            # フィルター条件を構築
            filters = {"user_id": user_id}
            if problem_id:
                filters["problem_id"] = problem_id
            if contest_id:
                filters["contest_id"] = contest_id

            submissions = await self.submission_repo.find_by_filters(filters, limit, offset)
            total_count = await self.submission_repo.count_by_filters(filters)

            submission_list = []
            for submission in submissions:
                submission_data = {
                    "submission_id": str(submission.id),
                    "problem_id": str(submission.problem_id),
                    "language": submission.language.value,
                    "status": submission.status.value,
                    "result": submission.overall_result.value if submission.overall_result else None,
                    "score": submission.total_points,
                    "max_score": submission.max_points,
                    "created_at": submission.submitted_at.isoformat(),
                    "judged_at": submission.judged_at.isoformat() if submission.judged_at else None,
                }

                if include_code:
                    submission_data["code"] = submission.code

                submission_list.append(submission_data)

            return {
                "success": True,
                "submissions": submission_list,
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": total_count > offset + limit,
                },
            }

        except Exception as e:
            logger.error(f"Failed to get user submissions: {e}")
            return {
                "success": False,
                "error": "Internal server error",
                "error_code": "INTERNAL_ERROR",
            }

    async def get_problem_submissions(
        self,
        problem_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
        contest_id: Optional[uuid.UUID] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """問題の提出一覧を取得（API用）"""
        try:
            filters = {"problem_id": problem_id}
            if user_id:
                filters["user_id"] = user_id
            if contest_id:
                filters["contest_id"] = contest_id

            submissions = await self.submission_repo.find_by_filters(filters, limit, offset)
            total_count = await self.submission_repo.count_by_filters(filters)

            submission_list = []
            for submission in submissions:
                # プライバシー保護のため、他のユーザーのコードは含めない
                submission_data = {
                    "submission_id": str(submission.id),
                    "user_id": str(submission.user_id) if user_id == submission.user_id else None,
                    "language": submission.language.value,
                    "status": submission.status.value,
                    "result": submission.overall_result.value if submission.overall_result else None,
                    "score": submission.total_points,
                    "created_at": submission.submitted_at.isoformat(),
                    "judged_at": submission.judged_at.isoformat() if submission.judged_at else None,
                }
                submission_list.append(submission_data)

            return {
                "success": True,
                "submissions": submission_list,
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": total_count > offset + limit,
                },
            }

        except Exception as e:
            logger.error(f"Failed to get problem submissions: {e}")
            return {
                "success": False,
                "error": "Internal server error",
                "error_code": "INTERNAL_ERROR",
            }

    async def rejudge_submission(
        self, 
        submission_id: uuid.UUID, 
        requester_user_id: uuid.UUID,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """提出を再ジャッジ（API用）"""
        try:
            # 権限チェック
            has_permission = await self._check_rejudge_permission(submission_id, requester_user_id)
            if not has_permission:
                return {
                    "success": False,
                    "error": "Permission denied",
                    "error_code": "PERMISSION_DENIED",
                }

            submission = await self.submission_repo.find_by_id(submission_id)
            if not submission:
                return {
                    "success": False,
                    "error": "Submission not found",
                    "error_code": "SUBMISSION_NOT_FOUND",
                }

            # 提出をリセット
            submission.status = ExecutionStatus.PENDING
            submission.overall_result = JudgeResult.PENDING
            submission.total_points = 0
            submission.judge_case_results = []
            submission.judged_at = None

            await self.submission_repo.save(submission)

            # キューに再追加
            queue_success = await self._enqueue_submission(submission, priority=5)  # 高優先度
            if not queue_success:
                return {
                    "success": False,
                    "error": "Failed to enqueue for rejudge",
                    "error_code": "REJUDGE_ENQUEUE_FAILED",
                }

            logger.info(f"Rejudge requested for submission {submission_id} by user {requester_user_id}")

            return {
                "success": True,
                "submission": {
                    "submission_id": str(submission.id),
                    "status": submission.status.value,
                    "rejudge_reason": reason,
                    "queue_position": await self._get_estimated_queue_position(submission_id),
                },
            }

        except Exception as e:
            logger.error(f"Failed to rejudge submission: {e}")
            return {
                "success": False,
                "error": "Internal server error",
                "error_code": "INTERNAL_ERROR",
            }

    # プライベートメソッド

    async def _validate_submission_request(
        self,
        user_id: uuid.UUID,
        problem_id: uuid.UUID,
        code: str,
        language: Language,
        contest_id: Optional[uuid.UUID],
    ) -> Dict[str, Any]:
        """提出リクエストのバリデーション"""
        try:
            # ユーザー存在確認
            user = await self.user_repo.find_by_id(user_id)
            if not user:
                return {"valid": False, "error": "User not found", "error_code": "USER_NOT_FOUND"}

            # 問題存在確認
            problem = await self.problem_repo.find_by_id(problem_id)
            if not problem:
                return {"valid": False, "error": "Problem not found", "error_code": "PROBLEM_NOT_FOUND"}

            # 問題公開状態確認
            if problem.status != "published":
                return {"valid": False, "error": "Problem not available", "error_code": "PROBLEM_NOT_AVAILABLE"}

            # コード長確認
            if len(code) > 100000:  # 100KB制限
                return {"valid": False, "error": "Code too long", "error_code": "CODE_TOO_LONG"}

            if len(code.strip()) == 0:
                return {"valid": False, "error": "Code cannot be empty", "error_code": "CODE_EMPTY"}

            # 言語サポート確認
            supported_languages = getattr(problem, 'supported_languages', [])
            if supported_languages and language not in supported_languages:
                return {"valid": False, "error": "Language not supported", "error_code": "LANGUAGE_NOT_SUPPORTED"}

            # コンテスト関連確認
            if contest_id:
                # コンテスト存在確認やエントリー確認はここで実装
                pass

            # レート制限確認（例：1分間に10回まで）
            recent_submissions = await self.submission_repo.count_recent_submissions(
                user_id, minutes=1
            )
            if recent_submissions >= 10:
                return {"valid": False, "error": "Too many submissions", "error_code": "RATE_LIMITED"}

            return {"valid": True}

        except Exception as e:
            logger.error(f"Validation error: {e}")
            return {"valid": False, "error": "Validation failed", "error_code": "VALIDATION_ERROR"}

    async def _create_submission(
        self,
        user_id: uuid.UUID,
        problem_id: uuid.UUID,
        code: str,
        language: Language,
        contest_id: Optional[uuid.UUID],
        metadata: Optional[Dict[str, Any]],
    ) -> Optional[Submission]:
        """提出を作成"""
        try:
            # ジャッジケースを取得して最大ポイントを計算
            judge_cases = await self.problem_repo.get_judge_cases(problem_id)
            max_points = sum(case.points for case in judge_cases)

            submission = Submission(
                id=uuid.uuid4(),
                problem_id=problem_id,
                user_id=user_id,
                code=code,
                language=language,
                status=ExecutionStatus.PENDING,
                overall_result=JudgeResult.PENDING,
                total_points=0,
                max_points=max_points,
                submitted_at=datetime.utcnow(),
                metadata=metadata or {},
            )

            if contest_id:
                submission.metadata["contest_id"] = str(contest_id)

            success = await self.submission_repo.save(submission)
            return submission if success else None

        except Exception as e:
            logger.error(f"Failed to create submission: {e}")
            return None

    async def _enqueue_submission(
        self, 
        submission: Submission, 
        contest_id: Optional[uuid.UUID] = None,
        priority: int = 1
    ) -> bool:
        """提出をキューに追加"""
        try:
            queue_item = JudgeQueue(
                id=uuid.uuid4(),
                submission_id=submission.id,
                priority=self._calculate_priority(submission, contest_id, priority),
                status=ExecutionStatus.PENDING,
                created_at=datetime.utcnow(),
            )

            return await self.queue_repo.save(queue_item)

        except Exception as e:
            logger.error(f"Failed to enqueue submission: {e}")
            return False

    async def _publish_submission_created_event(
        self, 
        submission: Submission, 
        contest_id: Optional[uuid.UUID]
    ) -> None:
        """提出作成イベントを発行"""
        try:
            event = SubmissionCreatedEvent(
                submission_id=submission.id,
                user_id=submission.user_id,
                problem_id=submission.problem_id,
                language=submission.language.value,
                created_at=submission.submitted_at,
                contest_id=contest_id,
            )
            self.event_bus.publish(event)

        except Exception as e:
            logger.error(f"Failed to publish submission created event: {e}")

    async def _get_estimated_queue_position(self, submission_id: uuid.UUID) -> Optional[int]:
        """推定キュー位置を取得"""
        try:
            queue_items = await self.queue_repo.find_pending_items(limit=1000)
            for i, item in enumerate(queue_items):
                if item.submission_id == submission_id:
                    return i + 1
            return None
        except Exception:
            return None

    def _calculate_priority(
        self, 
        submission: Submission, 
        contest_id: Optional[uuid.UUID],
        base_priority: int = 1
    ) -> int:
        """優先度を計算"""
        priority = base_priority

        # コンテスト中は優先度を上げる
        if contest_id:
            priority += 2

        # 再ジャッジは優先度を上げる
        if base_priority > 1:
            priority += 3

        return priority

    async def _check_rejudge_permission(
        self, 
        submission_id: uuid.UUID, 
        requester_user_id: uuid.UUID
    ) -> bool:
        """再ジャッジ権限をチェック"""
        try:
            submission = await self.submission_repo.find_by_id(submission_id)
            if not submission:
                return False

            # 自分の提出は再ジャッジ可能
            if submission.user_id == requester_user_id:
                return True

            # 管理者権限があれば再ジャッジ可能
            user = await self.user_repo.find_by_id(requester_user_id)
            if user and hasattr(user, 'role') and user.role in ['admin', 'moderator']:
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to check rejudge permission: {e}")
            return False