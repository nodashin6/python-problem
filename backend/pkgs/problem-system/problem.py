class BookEntity(Entity):
    """Problem book entity"""

    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="")
    author_id: UUID4
    is_published: bool = Field(default=False)
    cover_image_url: Optional[str] = None

    def publish(self) -> None:
        """Publish book"""
        self.is_published = True
        self.updated_at = datetime.utcnow()

    def unpublish(self) -> None:
        """Unpublish book"""
        self.is_published = False
        self.updated_at = datetime.utcnow()


class TagEntity(Entity):
    """Problem tag value object - aligned with actual DB schema"""

    id: UUID4 = Field()
    name: str = Field(..., min_length=1, max_length=50)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")

    @field_validator("name")
    def validate_name(cls, v):
        return v.strip().lower()


class ProblemEntity(Entity):
    """Problem entity"""

    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.EASY)
    status: ProblemStatus = Field(default=ProblemStatus.DRAFT)
    tags: Set[Tag] = Field(default_factory=set)
    metadata: ProblemMetadata = Field(default_factory=ProblemMetadata)
    author_id: UUID4
    book_id: Optional[UUID4] = None

    # Statistics
    submission_count: int = Field(default=0, ge=0)
    accepted_count: int = Field(default=0, ge=0)

    def __init__(self, **data):
        super().__init__(**data)
        self.add_event(ProblemCreated(problem_id=self.id, title=self.title, author_id=self.author_id))

    @property
    def acceptance_rate(self) -> float:
        """Calculate acceptance rate"""
        if self.submission_count == 0:
            return 0.0
        return round(self.accepted_count / self.submission_count * 100, 2)

    def add_tag(self, tag: Tag) -> None:
        """Add tag to problem"""
        self.tags.add(tag)
        self.updated_at = datetime.utcnow()

    def remove_tag(self, tag_name: str) -> None:
        """Remove tag from problem"""
        self.tags = {tag for tag in self.tags if tag.name != tag_name.lower()}
        self.updated_at = datetime.utcnow()

    def publish(self) -> None:
        """Publish problem"""
        if self.status == ProblemStatus.DRAFT:
            self.status = ProblemStatus.PUBLISHED
            self.updated_at = datetime.utcnow()
            self.add_event(ProblemPublished(problem_id=self.id, published_by=self.author_id))

    def archive(self) -> None:
        """Archive problem"""
        self.status = ProblemStatus.ARCHIVED
        self.updated_at = datetime.utcnow()

    def update_statistics(self, submission_count: int, accepted_count: int) -> None:
        """Update problem statistics"""
        self.submission_count = submission_count
        self.accepted_count = accepted_count
        self.updated_at = datetime.utcnow()


class ProblemMetadataEntity(Entity):
    """Problem metadata value object"""

    id: UUID4 = Field()
    time_limit_ms: int = Field(default=2000, ge=100, le=10000)
    memory_limit_mb: int = Field(default=256, ge=16, le=1024)
    expected_solution_length: Optional[int] = None
    hints: List[str] = Field(default_factory=list)


class ProblemContentEntity(Entity):
    """Problem content for internationalization"""

    problem_id: UUID4
    language: str = Field(..., min_length=2, max_length=5)
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    input_format: str = Field(default="")
    output_format: str = Field(default="")
    constraints: str = Field(default="")
    sample_explanation: str = Field(default="")
