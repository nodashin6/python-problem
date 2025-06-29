"""
Core Domain Models
コアドメインモデル - 抽象的な基底クラスのみ
"""

from .base import BaseModel, ValueObject

__all__ = [
    "BaseModel",
    "ValueObject",
]
