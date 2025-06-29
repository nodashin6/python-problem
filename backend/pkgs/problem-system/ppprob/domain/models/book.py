from typing import Any

from pydantic import UUID4, BaseModel, Field

from ..entities import BookEntity


class Book(BookEntity):
    """Book aggregate model that extends BookEntity with related data"""

    # BookEntityから継承されるフィールドを明示的に定義
    id: UUID4
    title: str
    description: str
    author_id: UUID4
    published_at: str | None = None
    archived_at: str | None = None
    created_at: str
    updated_at: str

    # 集約固有の関連データ
    author: Any = Field(description="Author information")  # UserEntityの代わりにAnyを使用
    problem_count: int = Field(default=0, description="Number of problems in this book")
    published_problem_count: int = Field(default=0, description="Number of published problems")
