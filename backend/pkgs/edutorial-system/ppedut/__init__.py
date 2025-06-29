"""
Edutorial System Package
解説システムパッケージ - 問題の解説管理

責任領域:
- 問題解説の作成・編集
- 多言語対応解説
- 解説の承認・公開
- 解説の検索・フィルタリング
- 解説の評価・コメント
"""

# Domain Models
# Domain Entities
from .domain.entities import EditorialContentEntity, EditorialEntity
from .domain.models import Editorial, EditorialContent

# Domain Services
from .domain.services import EditorialDomainService

# Use Cases
from .usecase import (
    CreateEditorialUseCase,
    PublishEditorialUseCase,
    TranslateEditorialUseCase,
)

__all__ = [
    # Models
    "Editorial",
    "EditorialContent",
    # Entities
    "EditorialEntity",
    "EditorialContentEntity",
    # Services
    "EditorialDomainService",
    # Use Cases
    "CreateEditorialUseCase",
    "PublishEditorialUseCase",
    "TranslateEditorialUseCase",
]
