"""
Event-driven architecture components
イベント駆動アーキテクチャコンポーネント
"""

import asyncio
import json
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, Callable, Awaitable
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import logging

from ..const import DomainType
from .logging import get_logger

logger = get_logger(__name__)


class EventPriority(Enum):
    """イベント優先度"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class DomainEvent:
    """ドメインイベントの基底クラス"""

    event_id: str
    event_type: str
    source_domain: DomainType
    target_domain: Optional[DomainType]
    occurred_at: datetime
    data: Dict[str, Any]
    priority: EventPriority = EventPriority.NORMAL
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
        if not self.occurred_at:
            self.occurred_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        data = asdict(self)
        data["occurred_at"] = self.occurred_at.isoformat()
        data["source_domain"] = self.source_domain.value if self.source_domain else None
        data["target_domain"] = self.target_domain.value if self.target_domain else None
        data["priority"] = self.priority.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DomainEvent":
        """辞書から復元"""
        data["occurred_at"] = datetime.fromisoformat(data["occurred_at"])
        data["source_domain"] = (
            DomainType(data["source_domain"]) if data["source_domain"] else None
        )
        data["target_domain"] = (
            DomainType(data["target_domain"]) if data["target_domain"] else None
        )
        data["priority"] = EventPriority(data["priority"])
        return cls(**data)


# Core Domain Events
@dataclass
class ProblemCreatedEvent(DomainEvent):
    """問題作成イベント"""

    def __init__(self, problem_id: str, title: str, difficulty: int, **kwargs):
        super().__init__(
            event_type="problem.created",
            source_domain=DomainType.CORE,
            target_domain=DomainType.JUDGE,
            data={"problem_id": problem_id, "title": title, "difficulty": difficulty},
            **kwargs,
        )


@dataclass
class ProblemUpdatedEvent(DomainEvent):
    """問題更新イベント"""

    def __init__(self, problem_id: str, changes: Dict[str, Any], **kwargs):
        super().__init__(
            event_type="problem.updated",
            source_domain=DomainType.CORE,
            target_domain=DomainType.JUDGE,
            data={"problem_id": problem_id, "changes": changes},
            **kwargs,
        )


@dataclass
class JudgeCaseUpdatedEvent(DomainEvent):
    """テストケース更新イベント"""

    def __init__(self, problem_id: str, judge_case_id: str, **kwargs):
        super().__init__(
            event_type="judgecase.updated",
            source_domain=DomainType.CORE,
            target_domain=DomainType.JUDGE,
            data={"problem_id": problem_id, "judge_case_id": judge_case_id},
            **kwargs,
        )


@dataclass
class UserRegisteredEvent(DomainEvent):
    """ユーザー登録イベント"""

    def __init__(self, user_id: str, email: str, username: str, **kwargs):
        super().__init__(
            event_type="user.registered",
            source_domain=DomainType.CORE,
            target_domain=None,  # 全ドメインに送信
            data={"user_id": user_id, "email": email, "username": username},
            **kwargs,
        )


# Judge Domain Events
@dataclass
class SubmissionCreatedEvent(DomainEvent):
    """提出作成イベント"""

    def __init__(
        self, submission_id: str, user_id: str, problem_id: str, language: str, **kwargs
    ):
        super().__init__(
            event_type="submission.created",
            source_domain=DomainType.JUDGE,
            target_domain=DomainType.CORE,
            data={
                "submission_id": submission_id,
                "user_id": user_id,
                "problem_id": problem_id,
                "language": language,
            },
            **kwargs,
        )


@dataclass
class JudgeStartedEvent(DomainEvent):
    """ジャッジ開始イベント"""

    def __init__(self, judge_id: str, submission_id: str, **kwargs):
        super().__init__(
            event_type="judge.started",
            source_domain=DomainType.JUDGE,
            target_domain=None,
            priority=EventPriority.HIGH,
            data={"judge_id": judge_id, "submission_id": submission_id},
            **kwargs,
        )


@dataclass
class JudgeCompletedEvent(DomainEvent):
    """ジャッジ完了イベント"""

    def __init__(
        self,
        judge_id: str,
        submission_id: str,
        result: str,
        score: Optional[float] = None,
        **kwargs,
    ):
        super().__init__(
            event_type="judge.completed",
            source_domain=DomainType.JUDGE,
            target_domain=DomainType.CORE,
            priority=EventPriority.HIGH,
            data={
                "judge_id": judge_id,
                "submission_id": submission_id,
                "result": result,
                "score": score,
            },
            **kwargs,
        )


@dataclass
class JudgeErrorEvent(DomainEvent):
    """ジャッジエラーイベント"""

    def __init__(self, judge_id: str, submission_id: str, error: str, **kwargs):
        super().__init__(
            event_type="judge.error",
            source_domain=DomainType.JUDGE,
            target_domain=DomainType.CORE,
            priority=EventPriority.CRITICAL,
            data={"judge_id": judge_id, "submission_id": submission_id, "error": error},
            **kwargs,
        )


# Event Handler
EventHandler = Callable[[DomainEvent], Awaitable[None]]


class EventSubscription:
    """イベント購読情報"""

    def __init__(
        self,
        event_type: str,
        handler: EventHandler,
        source_domain: Optional[DomainType] = None,
        priority_filter: Optional[EventPriority] = None,
    ):
        self.event_type = event_type
        self.handler = handler
        self.source_domain = source_domain
        self.priority_filter = priority_filter
        self.subscription_id = str(uuid.uuid4())


class EventBus:
    """イベントバス"""

    def __init__(self, max_queue_size: int = 1000):
        self.subscriptions: Dict[str, List[EventSubscription]] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self.dead_letter_queue: List[DomainEvent] = []
        self.is_running = False
        self._worker_task: Optional[asyncio.Task] = None
        self._stats = {"published": 0, "processed": 0, "failed": 0, "dead_letters": 0}

    async def start(self):
        """イベントバスを開始"""
        if self.is_running:
            return

        self.is_running = True
        self._worker_task = asyncio.create_task(self._process_events())
        logger.info("Event bus started")

    async def stop(self):
        """イベントバスを停止"""
        if not self.is_running:
            return

        self.is_running = False

        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass

        logger.info("Event bus stopped")

    def subscribe(
        self,
        event_type: str,
        handler: EventHandler,
        source_domain: Optional[DomainType] = None,
        priority_filter: Optional[EventPriority] = None,
    ) -> str:
        """イベントを購読"""
        subscription = EventSubscription(
            event_type, handler, source_domain, priority_filter
        )

        if event_type not in self.subscriptions:
            self.subscriptions[event_type] = []

        self.subscriptions[event_type].append(subscription)

        logger.info(f"Subscribed to event: {event_type} from {source_domain}")
        return subscription.subscription_id

    def unsubscribe(self, subscription_id: str):
        """購読を解除"""
        for event_type, subscriptions in self.subscriptions.items():
            self.subscriptions[event_type] = [
                sub for sub in subscriptions if sub.subscription_id != subscription_id
            ]

        logger.info(f"Unsubscribed: {subscription_id}")

    async def publish(self, event: DomainEvent):
        """イベントを発行"""
        try:
            await self.event_queue.put(event)
            self._stats["published"] += 1
            logger.debug(f"Event published: {event.event_type} ({event.event_id})")
        except asyncio.QueueFull:
            logger.error(f"Event queue full, dropping event: {event.event_id}")
            self.dead_letter_queue.append(event)
            self._stats["dead_letters"] += 1

    async def _process_events(self):
        """イベント処理ワーカー"""
        while self.is_running:
            try:
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                await self._handle_event(event)
                self.event_queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Event processing error: {e}")

    async def _handle_event(self, event: DomainEvent):
        """個別イベントを処理"""
        event_type = event.event_type

        if event_type not in self.subscriptions:
            logger.debug(f"No subscribers for event: {event_type}")
            return

        # 適用可能なハンドラーを取得
        applicable_handlers = []
        for subscription in self.subscriptions[event_type]:
            if self._should_handle_event(subscription, event):
                applicable_handlers.append(subscription.handler)

        if not applicable_handlers:
            logger.debug(f"No applicable handlers for event: {event_type}")
            return

        # 並行してハンドラーを実行
        tasks = [handler(event) for handler in applicable_handlers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 結果を処理
        success_count = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Event handler failed: {result}")
                self._stats["failed"] += 1
            else:
                success_count += 1

        if success_count > 0:
            self._stats["processed"] += 1

        logger.debug(
            f"Event processed: {event_type} ({success_count}/{len(applicable_handlers)} handlers succeeded)"
        )

    def _should_handle_event(
        self, subscription: EventSubscription, event: DomainEvent
    ) -> bool:
        """イベントがハンドラーで処理されるべきかチェック"""
        # ソースドメインフィルター
        if (
            subscription.source_domain
            and subscription.source_domain != event.source_domain
        ):
            return False

        # 優先度フィルター
        if (
            subscription.priority_filter
            and event.priority.value < subscription.priority_filter.value
        ):
            return False

        return True

    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        return {
            **self._stats,
            "queue_size": self.event_queue.qsize(),
            "subscriptions": sum(len(subs) for subs in self.subscriptions.values()),
            "dead_letter_count": len(self.dead_letter_queue),
        }


class EventStore:
    """イベントストア（簡易実装）"""

    def __init__(self):
        self.events: List[DomainEvent] = []

    async def append(self, event: DomainEvent):
        """イベントを追加"""
        self.events.append(event)

    async def get_events(
        self, aggregate_id: str, from_version: int = 0
    ) -> List[DomainEvent]:
        """特定の集約のイベントを取得"""
        return [
            event
            for event in self.events
            if event.data.get("aggregate_id") == aggregate_id
        ][from_version:]

    async def get_events_by_type(self, event_type: str) -> List[DomainEvent]:
        """特定のタイプのイベントを取得"""
        return [event for event in self.events if event.event_type == event_type]


# グローバルインスタンス
event_bus = EventBus()
event_store = EventStore()


# 便利関数
async def publish_event(event: DomainEvent):
    """イベントを発行（便利関数）"""
    await event_bus.publish(event)
    await event_store.append(event)


def subscribe_to_event(event_type: str, source_domain: Optional[DomainType] = None):
    """イベント購読デコレータ"""

    def decorator(handler: EventHandler):
        event_bus.subscribe(event_type, handler, source_domain)
        return handler

    return decorator
