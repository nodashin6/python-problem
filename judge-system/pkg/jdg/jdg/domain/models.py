"""
Judge Domain Models
ジャッジドメインモデル
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from ...shared.events import DomainEvent
from ...const import (
    ExecutionStatus,
    JudgeResultType as JudgeResult,
    ProgrammingLanguage as Language,
)


@dataclass
class ExecutionResult:
    """実行結果"""

    status: ExecutionStatus
    output: str = ""
    error: str = ""
    execution_time: float = 0.0  # 秒
    memory_usage: int = 0  # KB
    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""


@dataclass
class JudgeCaseResult:
    """ジャッジケース結果"""

    judge_case_id: uuid.UUID
    result: JudgeResult
    execution_result: ExecutionResult
    points: int = 0
    feedback: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Submission:
    """提出"""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    problem_id: uuid.UUID = field(default_factory=uuid.uuid4)
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)
    code: str = ""
    language: Language = Language.PYTHON
    status: ExecutionStatus = ExecutionStatus.PENDING
    overall_result: JudgeResult = JudgeResult.PENDING
    total_points: int = 0
    max_points: int = 0
    execution_time: float = 0.0
    memory_usage: int = 0
    judge_case_results: List[JudgeCaseResult] = field(default_factory=list)
    compile_error: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def add_judge_case_result(self, result: JudgeCaseResult) -> None:
        """ジャッジケース結果を追加"""
        self.judge_case_results.append(result)
        self.total_points += result.points
        self.execution_time = max(
            self.execution_time, result.execution_result.execution_time
        )
        self.memory_usage = max(self.memory_usage, result.execution_result.memory_usage)

    def update_overall_result(self) -> None:
        """全体結果を更新"""
        if not self.judge_case_results:
            self.overall_result = JudgeResult.PENDING
            return

        # すべてのケースが AC なら AC
        all_accepted = all(
            result.result == JudgeResult.ACCEPTED for result in self.judge_case_results
        )

        if all_accepted:
            self.overall_result = JudgeResult.ACCEPTED
        else:
            # 最初の非AC結果を採用
            for result in self.judge_case_results:
                if result.result != JudgeResult.ACCEPTED:
                    self.overall_result = result.result
                    break

    def is_finished(self) -> bool:
        """ジャッジが完了したか"""
        return self.status in [
            ExecutionStatus.COMPLETED,
            ExecutionStatus.FAILED,
            ExecutionStatus.TIMEOUT,
            ExecutionStatus.MEMORY_EXCEEDED,
            ExecutionStatus.CANCELLED,
        ]

    def get_score_percentage(self) -> float:
        """スコアの割合を取得"""
        if self.max_points == 0:
            return 0.0
        return (self.total_points / self.max_points) * 100


@dataclass
class CodeExecution:
    """コード実行"""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    code: str = ""
    language: Language = Language.PYTHON
    input_data: str = ""
    expected_output: str = ""
    time_limit: float = 1.0  # 秒
    memory_limit: int = 256  # MB
    status: ExecutionStatus = ExecutionStatus.PENDING
    result: Optional[ExecutionResult] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def set_result(self, result: ExecutionResult) -> None:
        """実行結果を設定"""
        self.result = result
        self.status = result.status
        self.updated_at = datetime.utcnow()


@dataclass
class JudgeQueue:
    """ジャッジキュー"""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    submission_id: uuid.UUID = field(default_factory=uuid.uuid4)
    priority: int = 0  # 優先度（大きいほど高優先度）
    retry_count: int = 0
    max_retries: int = 3
    status: ExecutionStatus = ExecutionStatus.PENDING
    assigned_worker: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def can_retry(self) -> bool:
        """リトライ可能か"""
        return self.retry_count < self.max_retries

    def increment_retry(self) -> None:
        """リトライ回数を増加"""
        self.retry_count += 1
        self.updated_at = datetime.utcnow()


# Domain Events


class SubmissionCreatedEvent(DomainEvent):
    """提出作成イベント"""

    def __init__(
        self,
        submission_id: uuid.UUID,
        problem_id: uuid.UUID,
        user_id: uuid.UUID,
        language: str,
        **kwargs
    ):
        data = {
            "submission_id": str(submission_id),
            "problem_id": str(problem_id),
            "user_id": str(user_id),
            "language": language,
        }
        super().__init__(
            event_id=kwargs.get("event_id", str(uuid.uuid4())),
            event_type="submission_created",
            source_domain="judge",
            target_domain=kwargs.get("target_domain"),
            occurred_at=kwargs.get("occurred_at", datetime.utcnow()),
            data=data,
            **{
                k: v
                for k, v in kwargs.items()
                if k not in ["event_id", "target_domain", "occurred_at"]
            }
        )
        self.submission_id = submission_id
        self.problem_id = problem_id
        self.user_id = user_id
        self.language = language


class SubmissionJudgedEvent(DomainEvent):
    """提出ジャッジ完了イベント"""

    def __init__(
        self,
        submission_id: uuid.UUID,
        problem_id: uuid.UUID,
        user_id: uuid.UUID,
        result: str,
        total_points: int,
        max_points: int,
        **kwargs
    ):
        data = {
            "submission_id": str(submission_id),
            "problem_id": str(problem_id),
            "user_id": str(user_id),
            "result": result,
            "total_points": total_points,
            "max_points": max_points,
        }
        super().__init__(
            event_id=kwargs.get("event_id", str(uuid.uuid4())),
            event_type="submission_judged",
            source_domain="judge",
            target_domain=kwargs.get("target_domain"),
            occurred_at=kwargs.get("occurred_at", datetime.utcnow()),
            data=data,
            **{
                k: v
                for k, v in kwargs.items()
                if k not in ["event_id", "target_domain", "occurred_at"]
            }
        )
        self.submission_id = submission_id
        self.problem_id = problem_id
        self.user_id = user_id
        self.result = result
        self.total_points = total_points
        self.max_points = max_points


class CodeExecutionStartedEvent(DomainEvent):
    """コード実行開始イベント"""

    def __init__(self, execution_id: uuid.UUID, language: str, **kwargs):
        data = {
            "execution_id": str(execution_id),
            "language": language,
        }
        super().__init__(
            event_id=kwargs.get("event_id", str(uuid.uuid4())),
            event_type="code_execution_started",
            source_domain="judge",
            target_domain=kwargs.get("target_domain"),
            occurred_at=kwargs.get("occurred_at", datetime.utcnow()),
            data=data,
            **{
                k: v
                for k, v in kwargs.items()
                if k not in ["event_id", "target_domain", "occurred_at"]
            }
        )
        self.execution_id = execution_id
        self.language = language


class CodeExecutionCompletedEvent(DomainEvent):
    """コード実行完了イベント"""

    def __init__(
        self,
        execution_id: uuid.UUID,
        status: str,
        execution_time: float,
        memory_usage: int,
        **kwargs
    ):
        data = {
            "execution_id": str(execution_id),
            "status": status,
            "execution_time": execution_time,
            "memory_usage": memory_usage,
        }
        super().__init__(
            event_id=kwargs.get("event_id", str(uuid.uuid4())),
            event_type="code_execution_completed",
            source_domain="judge",
            target_domain=kwargs.get("target_domain"),
            occurred_at=kwargs.get("occurred_at", datetime.utcnow()),
            data=data,
            **{
                k: v
                for k, v in kwargs.items()
                if k not in ["event_id", "target_domain", "occurred_at"]
            }
        )
        self.execution_id = execution_id
        self.status = status
        self.execution_time = execution_time
        self.memory_usage = memory_usage


class JudgeQueueUpdatedEvent(DomainEvent):
    """ジャッジキュー更新イベント"""

    def __init__(
        self,
        queue_id: uuid.UUID,
        status: str,
        assigned_worker: Optional[str] = None,
        **kwargs
    ):
        data = {
            "queue_id": str(queue_id),
            "status": status,
            "assigned_worker": assigned_worker,
        }
        super().__init__(
            event_id=kwargs.get("event_id", str(uuid.uuid4())),
            event_type="judge_queue_updated",
            source_domain="judge",
            target_domain=kwargs.get("target_domain"),
            occurred_at=kwargs.get("occurred_at", datetime.utcnow()),
            data=data,
            **{
                k: v
                for k, v in kwargs.items()
                if k not in ["event_id", "target_domain", "occurred_at"]
            }
        )
        self.queue_id = queue_id
        self.status = status
        self.assigned_worker = assigned_worker
