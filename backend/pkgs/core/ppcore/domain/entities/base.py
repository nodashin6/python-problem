"""
Base Entity for Core Domain (DEPRECATED)
コアドメイン基底エンティティ - Deprecated: Use ppcore.domain.base.BaseEntity instead
"""

from datetime import datetime
from uuid import uuid4

from pydantic import UUID4, ConfigDict, Field

# This class is deprecated in favor of ppcore.domain.base.BaseEntity
# Remove pydddi dependency to avoid external framework coupling


class BaseEntity:
    """
    Core domain base entity (DEPRECATED)
    DDDのEntityクラス - 永続化に焦点を当てたデータ構造
    
    WARNING: This class is deprecated. Use ppcore.domain.base.BaseEntity instead.
    This maintains backward compatibility but should be migrated.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, use_enum_values=True, validate_assignment=True)

    id: UUID4 = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def get_id(self) -> UUID4:
        """Get entity ID"""
        return self.id
