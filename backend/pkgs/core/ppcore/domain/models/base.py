"""
Base Model for Core Domain
コアドメイン基底モデル
"""

from abc import ABC
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import UUID4, ConfigDict, Field
from pydantic import BaseModel as PydanticBaseModel
from pydddi import IModel


class BaseModel(IModel, ABC):
    """
    Core domain base model
    DDDのModelクラス - ビジネスロジックを含む集約ルート
    """

    id: UUID4 = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        use_enum_values=True,
        validate_assignment=True,
    )

    # class Config:
    #     arbitrary_types_allowed = True
    #     use_enum_values = True
    #     validate_assignment = True

    def get_id(self) -> UUID4:
        """Get model ID"""
        return self.id

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return self.model_dump()


class ValueObject(PydanticBaseModel):
    """Value object base class"""

    model_config = ConfigDict(
        frozen=True,
        arbitrary_types_allowed=True,
    )

    # class Config:
    #     frozen = True
    #     arbitrary_types_allowed = True
