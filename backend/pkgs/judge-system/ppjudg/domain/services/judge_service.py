"""
Judge Domain Service
ジャッジドメインサービス
"""

import asyncio
import uuid
from datetime import datetime
from typing import Any

from ....const import (
    ExecutionStatus,
)
from ....const import (
    JudgeResultType as JudgeResult,
)
from ....const import (
    ProgrammingLanguage as Language,
)
from ....core.domain.repositories import JudgeCaseRepository
from ....shared.events import EventBus
from ....shared.logging import get_logger
from ..models import (
    CodeExecution,
    ExecutionResult,
    JudgeCaseResult,
    JudgeQueue,
    Submission,
)
from ..repositories import (
    CodeExecutionRepository,
    JudgeQueueRepository,
    SubmissionRepository,
)

logger = get_logger(__name__)


class JudgeDomainService:
    """ジャッジドメインサービス"""

    def __init__(
        self,
        submission_repo: SubmissionRepository,
        execution_repo: CodeExecutionRepository,
        queue_repo: JudgeQueueRepository,
        judge_case_repo: JudgeCaseRepository,
        event_bus: EventBus,
    ):
        self.submission_repo = submission_repo
        self.execution_repo = execution_repo
        self.queue_repo = queue_repo
        self.judge_case_repo = judge_case_repo
        self.event_bus = event_bus

    async def submit_code(
        self, user_id: uuid.UUID, problem_id: uuid.UUID, code: str, language: Language
    ) -> Submission:
        """コードを提出"""
        try:
            # 問題のジャッジケースを取得
            judge_cases = await self.judge_case_repo.find_by_problem(problem_id)
            if not judge_cases:
                raise ValueError(f"No judge cases found for problem {problem_id}")

            # 最大ポイントを計算
            max_points = sum(case.points for case in judge_cases)

            # 提出を作成
            submission = Submission(
                user_id=user_id,
                problem_id=problem_id,
                code=code,
                language=language,
                max_points=max_points,
            )

            # 提出を保存
            await self.submission_repo.save(submission)

            # ジャッジキューに追加
            queue_item = JudgeQueue(
                submission_id=submission.id,
                priority=self._calculate_priority(user_id, problem_id),
            )
            await self.queue_repo.save(queue_item)

            # イベントを発行
            from ..models import SubmissionCreatedEvent

            event = SubmissionCreatedEvent(
                submission_id=submission.id,
                problem_id=problem_id,
                user_id=user_id,
                language=language.value,
                timestamp=datetime.utcnow(),
            )
            await self.event_bus.publish(event)

            logger.info(f"Code submitted: {submission.id} by user {user_id}")
            return submission

        except Exception as e:
            logger.error(f"Failed to submit code: {e}")
            raise

    async def judge_submission(self, submission_id: uuid.UUID) -> bool:
        """提出をジャッジ"""
        try:
            # 提出を取得
            submission = await self.submission_repo.find_by_id(submission_id)
            if not submission:
                raise ValueError(f"Submission not found: {submission_id}")

            # ジャッジケースを取得
            judge_cases = await self.judge_case_repo.find_by_problem(
                submission.problem_id
            )
            if not judge_cases:
                raise ValueError(
                    f"No judge cases found for problem {submission.problem_id}"
                )

            # ジャッジ開始
            submission.status = ExecutionStatus.RUNNING
            await self.submission_repo.save(submission)

            # 各ジャッジケースを実行
            for judge_case in judge_cases:
                try:
                    # コード実行
                    execution = CodeExecution(
                        code=submission.code,
                        language=submission.language,
                        input_data=judge_case.input_data,
                        expected_output=judge_case.expected_output,
                        time_limit=(
                            judge_case.time_limit
                            if hasattr(judge_case, "time_limit")
                            else 1.0
                        ),
                        memory_limit=(
                            judge_case.memory_limit
                            if hasattr(judge_case, "memory_limit")
                            else 256
                        ),
                    )

                    # 実行結果を取得 (実際の実行は別のサービスで行う)
                    execution_result = await self._execute_code(execution)

                    # ジャッジ結果を評価
                    judge_result = self._evaluate_result(
                        execution_result, judge_case.expected_output
                    )

                    # ジャッジケース結果を作成
                    case_result = JudgeCaseResult(
                        judge_case_id=judge_case.id,
                        result=judge_result,
                        execution_result=execution_result,
                        points=(
                            judge_case.points
                            if judge_result == JudgeResult.ACCEPTED
                            else 0
                        ),
                    )

                    # 結果を提出に追加
                    submission.add_judge_case_result(case_result)

                    # 実行エラーの場合は即座に終了
                    if judge_result in [
                        JudgeResult.COMPILE_ERROR,
                        JudgeResult.INTERNAL_ERROR,
                    ]:
                        break

                except Exception as e:
                    logger.error(f"Error judging case {judge_case.id}: {e}")
                    # エラーケース結果を追加
                    error_result = ExecutionResult(
                        status=ExecutionStatus.FAILED, error=str(e)
                    )
                    case_result = JudgeCaseResult(
                        judge_case_id=judge_case.id,
                        result=JudgeResult.INTERNAL_ERROR,
                        execution_result=error_result,
                        points=0,
                    )
                    submission.add_judge_case_result(case_result)

            # 全体結果を更新
            submission.update_overall_result()
            submission.status = ExecutionStatus.COMPLETED
            await self.submission_repo.save(submission)

            # ジャッジ完了イベントを発行
            from ..models import SubmissionJudgedEvent

            event = SubmissionJudgedEvent(
                submission_id=submission.id,
                problem_id=submission.problem_id,
                user_id=submission.user_id,
                result=submission.overall_result.value,
                total_points=submission.total_points,
                max_points=submission.max_points,
                execution_time=submission.execution_time,
                timestamp=datetime.utcnow(),
            )
            await self.event_bus.publish(event)

            logger.info(
                f"Submission judged: {submission.id} - {submission.overall_result}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to judge submission {submission_id}: {e}")
            # エラー状態に更新
            if submission:
                submission.status = ExecutionStatus.FAILED
                await self.submission_repo.save(submission)
            return False

    async def execute_code(
        self,
        code: str,
        language: Language,
        input_data: str = "",
        time_limit: float = 1.0,
        memory_limit: int = 256,
    ) -> CodeExecution:
        """コードを実行"""
        try:
            # コード実行を作成
            execution = CodeExecution(
                code=code,
                language=language,
                input_data=input_data,
                time_limit=time_limit,
                memory_limit=memory_limit,
            )

            # 実行を保存
            await self.execution_repo.save(execution)

            # 実行開始イベントを発行
            from ..models import CodeExecutionStartedEvent

            event = CodeExecutionStartedEvent(
                execution_id=execution.id,
                language=language.value,
                timestamp=datetime.utcnow(),
            )
            await self.event_bus.publish(event)

            # 実際のコード実行
            execution_result = await self._execute_code(execution)
            execution.set_result(execution_result)

            # 実行結果を保存
            await self.execution_repo.save(execution)

            # 実行完了イベントを発行
            from ..models import CodeExecutionCompletedEvent

            event = CodeExecutionCompletedEvent(
                execution_id=execution.id,
                status=execution_result.status.value,
                execution_time=execution_result.execution_time,
                memory_usage=execution_result.memory_usage,
                timestamp=datetime.utcnow(),
            )
            await self.event_bus.publish(event)

            logger.info(f"Code executed: {execution.id} - {execution_result.status}")
            return execution

        except Exception as e:
            logger.error(f"Failed to execute code: {e}")
            raise

    async def get_user_submissions(
        self,
        user_id: uuid.UUID,
        problem_id: uuid.UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Submission]:
        """ユーザーの提出を取得"""
        try:
            if problem_id:
                return await self.submission_repo.find_by_user_and_problem(
                    user_id, problem_id
                )
            else:
                return await self.submission_repo.find_by_user(user_id, limit, offset)

        except Exception as e:
            logger.error(f"Failed to get user submissions for {user_id}: {e}")
            return []

    async def get_submission_statistics(self, user_id: uuid.UUID) -> dict[str, Any]:
        """提出統計を取得"""
        try:
            stats = await self.submission_repo.get_user_statistics(user_id)
            return stats

        except Exception as e:
            logger.error(f"Failed to get submission statistics for {user_id}: {e}")
            return {}

    async def get_judge_queue_status(self) -> dict[str, Any]:
        """ジャッジキューの状態を取得"""
        try:
            stats = await self.queue_repo.get_queue_statistics()
            return stats

        except Exception as e:
            logger.error(f"Failed to get judge queue status: {e}")
            return {}

    def _calculate_priority(self, user_id: uuid.UUID, problem_id: uuid.UUID) -> int:
        """ジャッジ優先度を計算"""
        # 基本優先度
        priority = 0

        # TODO: ユーザーの種類やプレミアム状態による優先度調整
        # TODO: 問題の難易度による優先度調整

        return priority

    async def _execute_code(self, execution: CodeExecution) -> ExecutionResult:
        """実際のコード実行 (モック実装)"""
        # TODO: 実際のサンドボックス実行環境との連携
        # 現在はモック実装

        # 実行開始
        execution.status = ExecutionStatus.RUNNING
        await self.execution_repo.save(execution)

        # 実行シミュレーション
        await asyncio.sleep(0.1)

        # 結果を作成 (モック)
        result = ExecutionResult(
            status=ExecutionStatus.COMPLETED,
            output="Hello, World!",
            execution_time=0.05,
            memory_usage=1024,
            exit_code=0,
            stdout="Hello, World!\n",
            stderr="",
        )

        return result

    def _evaluate_result(
        self, execution_result: ExecutionResult, expected_output: str
    ) -> JudgeResult:
        """実行結果を評価"""
        # 実行エラーチェック
        if execution_result.status == ExecutionStatus.TIMEOUT:
            return JudgeResult.TIME_LIMIT_EXCEEDED
        elif execution_result.status == ExecutionStatus.MEMORY_EXCEEDED:
            return JudgeResult.MEMORY_LIMIT_EXCEEDED
        elif execution_result.status == ExecutionStatus.FAILED:
            if execution_result.exit_code != 0:
                return JudgeResult.RUNTIME_ERROR
            else:
                return JudgeResult.INTERNAL_ERROR

        # 出力比較
        actual_output = execution_result.stdout.strip()
        expected_output = expected_output.strip()

        if actual_output == expected_output:
            return JudgeResult.ACCEPTED
        else:
            return JudgeResult.WRONG_ANSWER
