from pydddi import IModel


class Book(IModel):
    """
    Represents a book model.
    This class should contain fields that represent the book's properties.
    """

    id: str
    title: str
    description: str
    author_id: str
    published_at: str
    created_at: str
    updated_at: str

    def __str__(self) -> str:
        return f"Book(id={self.id}, title={self.title}, author_id={self.author_id})"
