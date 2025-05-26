"""
Submission Use Cases
提出ユースケース
"""

import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from ..domain.models import Submission, JudgeQueue
from ..domain.repositories.submission_repository import SubmissionRepository
from ..domain.repositories.judge_queue_repository import JudgeQueueRepository
from ..domain.services.judge_service import JudgeDomainService
from ...core.domain.repositories.problem_repository import ProblemRepository
from ...core.domain.repositories.user_repository import UserRepository
from ...const import (
    ProgrammingLanguage as Language,
    JudgeResultType as JudgeResult,
    ExecutionStatus,
)
from ...shared.events import DomainEventBus, SubmissionCreatedEvent


logger = logging.getLogger(__name__)


class SubmissionUseCase:
    """提出関連のユースケース"""

    def __init__(
        self,
        submission_repo: SubmissionRepository,
        queue_repo: JudgeQueueRepository,
        problem_repo: ProblemRepository,
        user_repo: UserRepository,
        judge_service: JudgeDomainService,
        event_bus: DomainEventBus,
    ):
        self.submission_repo = submission_repo
        self.queue_repo = queue_repo
        self.problem_repo = problem_repo
        self.user_repo = user_repo
        self.judge_service = judge_service
        self.event_bus = event_bus

    async def create_submission(
        self,
        user_id: uuid.UUID,
        problem_id: uuid.UUID,
        code: str,
        language: Language,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Submission]:
        """新しい提出を作成"""
        try:
            # ユーザーの存在確認
            user = await self.user_repo.find_by_id(user_id)
            if not user:
                logger.warning(f"User not found: {user_id}")
                return None

            # 問題の存在確認
            problem = await self.problem_repo.find_by_id(problem_id)
            if not problem:
                logger.warning(f"Problem not found: {problem_id}")
                return None

            # 問題が公開されているかチェック
            if problem.status != "published":
                logger.warning(f"Problem {problem_id} is not published")
                return None

            # ジャッジケースを取得して最大ポイントを計算
            judge_cases = await self.problem_repo.get_judge_cases(problem_id)
            max_points = sum(case.points for case in judge_cases)

            # 提出を作成
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

            # 提出を保存
            success = await self.submission_repo.save(submission)
            if not success:
                logger.error(f"Failed to save submission: {submission.id}")
                return None

            # ジャッジキューに追加
            queue_item = JudgeQueue(
                id=uuid.uuid4(),
                submission_id=submission.id,
                priority=self._calculate_priority(user, problem),
                status=ExecutionStatus.PENDING,
                created_at=datetime.utcnow(),
            )

            queue_success = await self.queue_repo.save(queue_item)
            if not queue_success:
                logger.error(f"Failed to add submission to queue: {submission.id}")
                # 提出は作成されているので、状態を記録
                submission.metadata["queue_error"] = True
                await self.submission_repo.save(submission)

            # ドメインイベントを発行
            event = SubmissionCreatedEvent(
                submission_id=submission.id,
                user_id=user_id,
                problem_id=problem_id,
                language=language.value,
                created_at=submission.submitted_at,
            )
            self.event_bus.publish(event)

            logger.info(f"Submission created successfully: {submission.id}")
            return submission

        except Exception as e:
            logger.error(f"Failed to create submission: {e}")
            return None

    async def get_submission(self, submission_id: uuid.UUID) -> Optional[Submission]:
        """提出を取得"""
        return await self.submission_repo.find_by_id(submission_id)

    async def get_user_submissions(
        self, user_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> List[Submission]:
        """ユーザーの提出一覧を取得"""
        return await self.submission_repo.find_by_user(user_id, limit, offset)

    async def get_problem_submissions(
        self, problem_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> List[Submission]:
        """問題の提出一覧を取得"""
        return await self.submission_repo.find_by_problem(problem_id, limit, offset)

    async def get_user_problem_submissions(
        self, user_id: uuid.UUID, problem_id: uuid.UUID
    ) -> List[Submission]:
        """ユーザーの特定問題に対する提出一覧を取得"""
        return await self.submission_repo.find_by_user_and_problem(user_id, problem_id)

    async def get_recent_submissions(self, limit: int = 50) -> List[Submission]:
        """最近の提出一覧を取得"""
        return await self.submission_repo.find_recent(limit)

    async def get_submissions_by_status(
        self, status: ExecutionStatus, limit: int = 50
    ) -> List[Submission]:
        """ステータス別の提出一覧を取得"""
        return await self.submission_repo.find_by_status(status, limit)

    async def get_submissions_by_result(
        self, result: JudgeResult, limit: int = 50
    ) -> List[Submission]:
        """結果別の提出一覧を取得"""
        return await self.submission_repo.find_by_result(result, limit)

    async def get_user_best_submissions(
        self, user_id: uuid.UUID, problem_ids: List[uuid.UUID]
    ) -> List[Submission]:
        """ユーザーの最高得点提出を取得"""
        return await self.submission_repo.find_user_best_submissions(
            user_id, problem_ids
        )

    async def get_user_statistics(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """ユーザーの提出統計を取得"""
        return await self.submission_repo.get_user_statistics(user_id)

    async def get_problem_statistics(self, problem_id: uuid.UUID) -> Dict[str, Any]:
        """問題の提出統計を取得"""
        return await self.submission_repo.get_problem_statistics(problem_id)

    async def rejudge_submission(self, submission_id: uuid.UUID) -> bool:
        """提出を再ジャッジ"""
        try:
            submission = await self.submission_repo.find_by_id(submission_id)
            if not submission:
                logger.warning(f"Submission not found for rejudge: {submission_id}")
                return False

            # ステータスをペンディングに戻す
            submission.status = ExecutionStatus.PENDING
            submission.overall_result = JudgeResult.PENDING
            submission.total_points = 0
            submission.judge_case_results = []
            submission.judged_at = None

            # 提出を更新
            success = await self.submission_repo.save(submission)
            if not success:
                return False

            # 既存のキューアイテムを確認
            existing_queue = await self.queue_repo.find_by_submission(submission_id)

            if existing_queue:
                # 既存アイテムのステータスを更新
                await self.queue_repo.update_status(
                    existing_queue.id, ExecutionStatus.PENDING
                )
            else:
                # 新しいキューアイテムを作成
                queue_item = JudgeQueue(
                    id=uuid.uuid4(),
                    submission_id=submission_id,
                    priority=5,  # 再ジャッジは高優先度
                    status=ExecutionStatus.PENDING,
                    created_at=datetime.utcnow(),
                )
                await self.queue_repo.save(queue_item)

            logger.info(f"Submission queued for rejudge: {submission_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to rejudge submission {submission_id}: {e}")
            return False

    async def delete_submission(self, submission_id: uuid.UUID) -> bool:
        """提出を削除"""
        try:
            # キューからも削除
            queue_item = await self.queue_repo.find_by_submission(submission_id)
            if queue_item:
                await self.queue_repo.delete(queue_item.id)

            # 提出を削除
            success = await self.submission_repo.delete(submission_id)

            if success:
                logger.info(f"Submission deleted: {submission_id}")

            return success

        except Exception as e:
            logger.error(f"Failed to delete submission {submission_id}: {e}")
            return False

    def _calculate_priority(self, user, problem) -> int:
        """提出の優先度を計算"""
        # デフォルト優先度
        priority = 1

        # ユーザーロールに基づく調整
        if hasattr(user, "role"):
            if user.role == "admin":
                priority += 3
            elif user.role == "moderator":
                priority += 2

        # 問題難易度に基づく調整
        if hasattr(problem, "difficulty"):
            if problem.difficulty == "very_easy":
                priority += 1

        return priority


class SubmissionJudgeUseCase:
    """提出ジャッジ関連のユースケース"""

    def __init__(
        self,
        submission_repo: SubmissionRepository,
        queue_repo: JudgeQueueRepository,
        problem_repo: ProblemRepository,
        judge_service: JudgeDomainService,
        event_bus: DomainEventBus,
    ):
        self.submission_repo = submission_repo
        self.queue_repo = queue_repo
        self.problem_repo = problem_repo
        self.judge_service = judge_service
        self.event_bus = event_bus

    async def process_submission(
        self, submission_id: uuid.UUID, worker_id: str
    ) -> bool:
        """提出をジャッジ処理"""
        try:
            # 提出を取得
            submission = await self.submission_repo.find_by_id(submission_id)
            if not submission:
                logger.error(f"Submission not found: {submission_id}")
                return False

            # 問題を取得
            problem = await self.problem_repo.find_by_id(submission.problem_id)
            if not problem:
                logger.error(f"Problem not found: {submission.problem_id}")
                return False

            # ジャッジケースを取得
            judge_cases = await self.problem_repo.get_judge_cases(submission.problem_id)
            if not judge_cases:
                logger.error(
                    f"No judge cases found for problem: {submission.problem_id}"
                )
                return False

            # ドメインサービスでジャッジ実行
            judge_success = await self.judge_service.process_submission(
                submission, judge_cases
            )

            if judge_success:
                # 提出を保存
                await self.submission_repo.save(submission)

                # キューステータスを完了に更新
                queue_item = await self.queue_repo.find_by_submission(submission_id)
                if queue_item:
                    await self.queue_repo.update_status(
                        queue_item.id, ExecutionStatus.COMPLETED
                    )

                logger.info(f"Submission judged successfully: {submission_id}")
                return True
            else:
                logger.error(f"Failed to judge submission: {submission_id}")
                return False

        except Exception as e:
            logger.error(f"Failed to process submission {submission_id}: {e}")
            return False
