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
    CryptographyHelper,
    DateTimeHelper,
    ValidationHelper,
)
from .domain.interfaces import IDomainService, IRepository

# Infrastructure abstractions (optional import)
try:
    from .infrastructure import CacheConnection, DatabaseConnection
except ImportError:
    # Infrastructure dependencies not available
    CacheConnection = None
    DatabaseConnection = None

# Queue system abstractions
from .queue import QMessage, QResponse, QueueService

__all__ = [
    # Base DDD classes
    "BaseEntity",
    "BaseModel",
    "BaseValueObject",
    "IRepository",
    "IDomainService",
    # Common helpers
    "DateTimeHelper",
    "ValidationHelper",
    "CryptographyHelper",
    # Queue abstractions
    "QueueService",
    "QMessage",
    "QResponse",
    # Infrastructure
    "DatabaseConnection",
    "CacheConnection",
]
