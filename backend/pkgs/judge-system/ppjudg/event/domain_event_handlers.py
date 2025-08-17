"""
Domain Event Handlers
ドメインイベントハンドラー

ドメインイベントから呼び出される処理を実装
従来の handlers.py の内容をここに移行
"""

from typing import Any

from dependency_injector.wiring import Provide, inject

# Local definitions to avoid cross-package dependencies
from typing import Protocol

class DomainType:
    """Domain type constants - local definition"""
    CORE = "core"
    JUDGE = "judge"

class EventBus(Protocol):
    """Event bus protocol - local definition"""
    async def publish(self, event): ...

# Event classes - local definitions
class JudgeCaseUpdatedEvent:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class JudgeCompletedEvent:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class JudgeErrorEvent:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class JudgeStartedEvent:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class ProblemCreatedEvent:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class ProblemUpdatedEvent:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class SubmissionCreatedEvent:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class UserRegisteredEvent:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

# Local logger function
def get_logger(name):
    import logging
    return logging.getLogger(name)

# Local use case protocols
class JudgeWorkerUseCase(Protocol):
    """Judge worker use case protocol - local definition"""
    pass

class SubmissionUseCase(Protocol):
    """Submission use case protocol - local definition"""  
    pass

logger = get_logger(__name__)


class CoreDomainEventHandler:
    """Coreドメインイベントハンドラー"""

    # @inject - temporarily disabled for testing
    def __init__(
        self,
        submission_use_case: SubmissionUseCase,
        event_bus: EventBus,
    ):
        self.submission_use_case = submission_use_case
        self.event_bus = event_bus
        # 非同期のセットアップは初期化後に別途呼び出す必要がある

    async def _setup_subscriptions(self):
        """イベント購読を設定"""
        # Coreドメインからのイベントを購読
        await self.event_bus.subscribe(
            "problem.created",
            self.handle_problem_created,
            source_domain=DomainType.CORE,
        )

        await self.event_bus.subscribe(
            "problem.updated",
            self.handle_problem_updated,
            source_domain=DomainType.CORE,
        )

        await self.event_bus.subscribe(
            "judgecase.updated",
            self.handle_judge_case_updated,
            source_domain=DomainType.CORE,
        )

        await self.event_bus.subscribe(
            "user.registered",
            self.handle_user_registered,
            source_domain=DomainType.CORE,
        )

    async def handle_problem_created(self, event: ProblemCreatedEvent):
        """問題作成イベントの処理"""
        try:
            problem_id = event.data["problem_id"]
            title = event.data["title"]
            difficulty = event.data["difficulty"]

            logger.info(f"Handling problem created: {problem_id} - {title}")

            # ジャッジシステム側で必要な初期化処理があれば実行
            # 例: 問題固有のジャッジ設定の準備など

            # 今のところ特別な処理は不要だが、将来的に拡張可能
            logger.debug(f"Problem {problem_id} ready for submissions")

        except Exception as e:
            logger.error(f"Failed to handle problem created event: {e}")

    async def handle_problem_updated(self, event: ProblemUpdatedEvent):
        """問題更新イベントの処理"""
        try:
            problem_id = event.data["problem_id"]
            changes = event.data["changes"]

            logger.info(f"Handling problem updated: {problem_id}")

            # テストケースが更新された場合は再ジャッジを検討
            if "judge_cases" in changes or "time_limit" in changes or "memory_limit" in changes:
                logger.info(f"Problem {problem_id} judge configuration changed, considering rejudge")

                # 管理者による明示的な再ジャッジ指示がある場合のみ実行
                if changes.get("force_rejudge", False):
                    await self._rejudge_problem_submissions(problem_id, "Problem configuration updated")

        except Exception as e:
            logger.error(f"Failed to handle problem updated event: {e}")

    async def handle_judge_case_updated(self, event: JudgeCaseUpdatedEvent):
        """ジャッジケース更新イベントの処理"""
        try:
            problem_id = event.data["problem_id"]
            judge_case_id = event.data["judge_case_id"]

            logger.info(f"Handling judge case updated: {judge_case_id} for problem {problem_id}")

            # ジャッジケース更新時の処理
            # 通常は管理者の判断で再ジャッジを実行
            logger.debug(f"Judge case {judge_case_id} updated, manual rejudge may be required")

        except Exception as e:
            logger.error(f"Failed to handle judge case updated event: {e}")

    async def handle_user_registered(self, event: UserRegisteredEvent):
        """ユーザー登録イベントの処理"""
        try:
            user_id = event.data["user_id"]
            user_name = event.data["user_name"]

            logger.info(f"Handling user registered: {user_id} ({user_name})")

            # ジャッジシステム側でのユーザー関連初期化があれば実行
            # 今のところ特別な処理は不要

        except Exception as e:
            logger.error(f"Failed to handle user registered event: {e}")

    async def _rejudge_problem_submissions(self, problem_id: str, reason: str):
        """問題の全提出を再ジャッジ"""
        try:
            # 最近の提出のみを対象とする (例: 過去30日)
            await self.submission_use_case.rejudge_problem_submissions(
                problem_id=problem_id, reason=reason, days_limit=30
            )

            logger.info(f"Rejudge initiated for problem {problem_id}: {reason}")

        except Exception as e:
            logger.error(f"Failed to rejudge problem submissions: {e}")


class JudgeSystemEventHandler:
    """ジャッジシステム内部イベントハンドラー"""

    # @inject - temporarily disabled for testing
    def __init__(
        self,
        worker_use_case: JudgeWorkerUseCase,
        event_bus: EventBus,
    ):
        self.worker_use_case = worker_use_case
        self.event_bus = event_bus
        # 非同期のセットアップは初期化後に別途呼び出す必要がある

    async def _setup_subscriptions(self):
        """イベント購読を設定"""
        # ジャッジシステム内部イベントを購読
        await self.event_bus.subscribe(
            "submission.created",
            self.handle_submission_created,
            source_domain=DomainType.JUDGE,
        )

        await self.event_bus.subscribe("judge.started", self.handle_judge_started, source_domain=DomainType.JUDGE)

        await self.event_bus.subscribe(
            "judge.completed",
            self.handle_judge_completed,
            source_domain=DomainType.JUDGE,
        )

        await self.event_bus.subscribe("judge.error", self.handle_judge_error, source_domain=DomainType.JUDGE)

    async def handle_submission_created(self, event: SubmissionCreatedEvent):
        """提出作成イベントの処理"""
        try:
            submission_id = event.data["submission_id"]
            user_id = event.data["user_id"]
            problem_id = event.data["problem_id"]

            logger.info(
                f"Handling submission created: {submission_id} by user {user_id} for problem {problem_id}"
            )

            # 特別な処理が必要な場合のロジック
            # 例: 特定ユーザーの優先処理、コンテスト期間中の処理など

        except Exception as e:
            logger.error(f"Failed to handle submission created event: {e}")

    async def handle_judge_started(self, event: JudgeStartedEvent):
        """ジャッジ開始イベントの処理"""
        try:
            judge_id = event.data["judge_id"]
            submission_id = event.data["submission_id"]

            logger.info(f"Judge started: {judge_id} for submission {submission_id}")

            # ジャッジ開始時の追加処理
            # 例: 進行状況の通知、リアルタイム更新など

        except Exception as e:
            logger.error(f"Failed to handle judge started event: {e}")

    async def handle_judge_completed(self, event: JudgeCompletedEvent):
        """ジャッジ完了イベントの処理"""
        try:
            judge_id = event.data["judge_id"]
            submission_id = event.data["submission_id"]
            result = event.data["result"]
            score = event.data.get("score")

            logger.info(f"Judge completed: {judge_id} for submission {submission_id} - Result: {result}")

            # ジャッジ完了時の追加処理
            # 例: 統計情報の更新、ランキングの更新、通知送信など

            # コンテスト中であれば順位表の更新
            await self._update_contest_standings_if_needed(submission_id, result, score)

            # ユーザー統計の更新
            await self._update_user_statistics(event.data["user_id"], result, score)

        except Exception as e:
            logger.error(f"Failed to handle judge completed event: {e}")

    async def handle_judge_error(self, event: JudgeErrorEvent):
        """ジャッジエラーイベントの処理"""
        try:
            judge_id = event.data["judge_id"]
            submission_id = event.data["submission_id"]
            error = event.data["error"]

            logger.error(f"Judge error: {judge_id} for submission {submission_id} - Error: {error}")

            # エラー時の処理
            # 例: 管理者通知、自動リトライ、エラー統計の更新など

            # 重要なエラーの場合は管理者に通知
            if self._is_critical_error(error):
                await self._notify_administrators(judge_id, submission_id, error)

            # リトライ可能なエラーの場合は再キューイング
            if self._is_retryable_error(error):
                await self._schedule_retry(submission_id, error)

        except Exception as e:
            logger.error(f"Failed to handle judge error event: {e}")

    async def _update_contest_standings_if_needed(
        self, submission_id: str, result: str, score: float | None
    ):
        """コンテスト順位表の更新 (必要な場合)"""
        try:
            # コンテスト機能が実装された際のプレースホルダー
            logger.debug("Contest standings update not implemented yet")

        except Exception as e:
            logger.error(f"Failed to update contest standings: {e}")

    async def _update_user_statistics(self, user_id: str, result: str, score: float | None):
        """ユーザー統計の更新"""
        try:
            # ユーザー統計更新のプレースホルダー
            # 実装はCoreドメインとの連携が必要
            logger.debug(f"User statistics update for {user_id}: {result}")

        except Exception as e:
            logger.error(f"Failed to update user statistics: {e}")

    def _is_critical_error(self, error: str) -> bool:
        """重要なエラーかどうかを判定"""
        critical_keywords = [
            "system failure",
            "database error",
            "memory error",
            "internal server error",
        ]

        error_lower = error.lower()
        return any(keyword in error_lower for keyword in critical_keywords)

    def _is_retryable_error(self, error: str) -> bool:
        """リトライ可能なエラーかどうかを判定"""
        retryable_keywords = [
            "timeout",
            "temporary failure",
            "network error",
            "resource temporarily unavailable",
        ]

        error_lower = error.lower()
        return any(keyword in error_lower for keyword in retryable_keywords)

    async def _notify_administrators(self, judge_id: str, submission_id: str, error: str):
        """管理者に通知"""
        try:
            # 管理者通知機能のプレースホルダー
            logger.warning(
                f"Critical judge error notification: Judge {judge_id}, Submission {submission_id}, Error: {error}"
            )

        except Exception as e:
            logger.error(f"Failed to notify administrators: {e}")

    async def _schedule_retry(self, submission_id: str, error: str):
        """リトライをスケジュール"""
        try:
            # リトライ機能のプレースホルダー
            logger.info(f"Scheduling retry for submission {submission_id} due to: {error}")

        except Exception as e:
            logger.error(f"Failed to schedule retry: {e}")


# イベントハンドラーのファクトリー
class EventHandlerFactory:
    """イベントハンドラーファクトリー"""

    @staticmethod
    def create_handlers() -> dict[str, Any]:
        """全てのイベントハンドラーを作成"""
        return {
            "core_domain_handler": CoreDomainEventHandler(),
            "judge_system_handler": JudgeSystemEventHandler(),
        }

    @staticmethod
    async def initialize_handlers():
        """イベントハンドラーを初期化"""
        try:
            handlers = EventHandlerFactory.create_handlers()
            logger.info("Event handlers initialized successfully")
            return handlers

        except Exception as e:
            logger.error(f"Failed to initialize event handlers: {e}")
            raise


# 便利関数
async def setup_event_handlers():
    """イベントハンドラーを設定"""
    return await EventHandlerFactory.initialize_handlers()
