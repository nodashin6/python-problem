from pydantic import UUID4, Field, BaseModel, ConfigDict

from ..value_objects.author_info import AuthorInfo


class Book(BaseModel):
    """
    Book aggregate model that extends BookEntity with related data
    Remove pydddi dependency and ppauth cross-module dependency
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True, use_enum_values=True, validate_assignment=True)

    # BookEntityから継承されるフィールドを明示的に定義
    id: UUID4
    title: str
    description: str
    author_id: UUID4
    published_at: str | None = None
    archived_at: str | None = None
    created_at: str
    updated_at: str

    # 集約固有の関連データ - 外部依存を排除
    author: AuthorInfo | None = Field(default=None, description="Author information as value object")
    problem_count: int = Field(default=0, description="Number of problems in this book")
    published_problem_count: int = Field(default=0, description="Number of published problems")
    
    def get_id(self) -> UUID4:
        """Get book ID"""
        return self.id
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return self.model_dump()
