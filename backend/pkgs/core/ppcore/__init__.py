"""
Core Package - Abstract Design and Common Functions
コアパッケージ - 抽象設計と汎用関数提供

責任領域:
- 基底クラス・インターフェース
- 共通ヘルパー・ユーティリティ
- DDDの基本構造
- キューシステムの抽象化
"""

# Base classes for DDD
from .domain.base import BaseEntity, BaseModel, BaseValueObject

# Common helpers
from .domain.helpers import (
    DateTimeHelper,
    ValidationHelper,
)
from .infrastructure.supabase import dependencies

# Queue system abstractions
from .queue import QMessage, QResponse, QueueService

__all__ = [
    "BaseEntity",
    "BaseModel",
    "BaseValueObject",
    "DateTimeHelper",
    "ValidationHelper",
    "QMessage",
    "QResponse",
    "QueueService",
    "dependencies",
]
