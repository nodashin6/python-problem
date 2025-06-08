class Editorial(Entity):
    """Editorial entity"""

    problem_id: UUID4
    author_id: UUID4
    is_published: bool = Field(default=False)

    def publish(self) -> None:
        """Publish editorial"""
        self.is_published = True
        self.updated_at = datetime.utcnow()


class EditorialContent(Entity):
    """Editorial content for internationalization"""

    editorial_id: UUID4
    language: str = Field(..., min_length=2, max_length=5)
    content: str = Field(..., min_length=1)
    approach: str = Field(default="")
    complexity_analysis: str = Field(default="")
    code_samples: Dict[str, str] = Field(default_factory=dict)  # language -> code


# Legacy compatibility (keeping the old models for migration)
class Content(Entity):
    """Content entity for various content types"""

    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    content_type: str = Field(
        ..., min_length=1
    )  # Using string instead of ContentType enum for now
    author_id: UUID4
    is_published: bool = Field(default=False)
    language: str = Field(default="en", min_length=2, max_length=5)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def publish(self) -> None:
        """Publish content"""
        self.is_published = True
        self.updated_at = datetime.utcnow()

    def unpublish(self) -> None:
        """Unpublish content"""
        self.is_published = False
        self.updated_at = datetime.utcnow()
