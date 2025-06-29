"""
Base Entity for Core Domain
コアドメイン基底エンティティ
"""

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import UUID4, Field
from pydddi import IEntity


class BaseEntity(IEntity[UUID4]):
    """
    Core domain base entity
    DDDのEntityクラス - 永続化に焦点を当てたデータ構造
    """

    id: UUID4 = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        arbitrary_types_allowed = True
        use_enum_values = True
        validate_assignment = True

    def get_id(self) -> UUID4:
        """Get entity ID"""
        return self.id
