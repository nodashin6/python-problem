"""
Core Domain Base Classes
コアドメイン基底クラス群 - 全パッケージで共通利用
"""

from abc import ABC
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import UUID4, ConfigDict, Field
from pydantic import BaseModel as PydanticBaseModel


class BaseValueObject(PydanticBaseModel):
    """
    Base Value Object
    値オブジェクト基底クラス - 不変オブジェクト
    """

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)


class BaseEntity(PydanticBaseModel):
    """
    Base Entity
    エンティティ基底クラス - 永続化用データ構造
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, use_enum_values=True, validate_assignment=True)

    id: UUID4 = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def get_id(self) -> UUID4:
        """Get entity ID"""
        return self.id


class BaseModel(PydanticBaseModel, ABC):
    """
    Base Model (Aggregate Root)
    モデル基底クラス - ビジネスロジックを含む集約ルート
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, use_enum_values=True, validate_assignment=True)

    id: UUID4 = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)

    def get_id(self) -> UUID4:
        """Get model ID"""
        return self.id

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return self.model_dump()
