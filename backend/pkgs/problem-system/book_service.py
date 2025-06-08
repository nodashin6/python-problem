"""
Book domain service
"""

from typing import List, Optional
from uuid import UUID

from ..models import Book, Problem
from ..repositories import BookRepository, ProblemRepository
from ....shared.events import EventBus


class BookDomainService:
    """Book domain service for book-related business logic"""

    def __init__(
        self,
        book_repo: BookRepository,
        problem_repo: ProblemRepository,
        event_bus: EventBus,
    ):
        self.book_repo = book_repo
        self.problem_repo = problem_repo
        self.event_bus = event_bus

    async def create_book(
        self,
        title: str,
        description: str,
        author_id: UUID,
        cover_image_url: Optional[str] = None,
    ) -> Book:
        """Create a new book"""
        # Check for duplicate title
        existing = await self.book_repo.find_by_title(title)
        if existing:
            raise ValueError("Book with this title already exists")

        # Create book entity
        book = Book(
            title=title,
            description=description,
            author_id=author_id,
            cover_image_url=cover_image_url,
        )

        return await self.book_repo.create(book)

    async def add_problem_to_book(self, book_id: UUID, problem_id: UUID) -> bool:
        """Add a problem to a book"""
        # Verify book exists
        book = await self.book_repo.get(book_id)
        if not book:
            return False

        # Verify problem exists and update its book_id
        problem = await self.problem_repo.get(problem_id)
        if not problem:
            return False

        # Update problem's book_id
        await self.problem_repo.update(problem_id, {"book_id": book_id})

        return True

    async def remove_problem_from_book(self, problem_id: UUID) -> bool:
        """Remove a problem from its book"""
        problem = await self.problem_repo.get(problem_id)
        if not problem:
            return False

        await self.problem_repo.update(problem_id, {"book_id": None})
        return True

    async def get_book_problems(self, book_id: UUID) -> List[Problem]:
        """Get all problems in a book"""
        return await self.problem_repo.find_by_book(book_id)

    async def publish_book(self, book_id: UUID) -> bool:
        """Publish a book and all its problems"""
        book = await self.book_repo.get(book_id)
        if not book:
            return False

        # Get all problems in the book
        problems = await self.problem_repo.find_by_book(book_id)

        # Validate all problems are ready for publishing
        for problem in problems:
            if problem.status.value != "published":
                raise ValueError(f"Problem '{problem.title}' is not ready for publishing")

        # Publish book
        book.publish()
        await self.book_repo.update(book_id, book)

        return True

    async def calculate_book_statistics(self, book_id: UUID) -> dict:
        """Calculate book statistics"""
        problems = await self.problem_repo.find_by_book(book_id)

        total_problems = len(problems)
        published_problems = len([p for p in problems if p.status.value == "published"])
        total_submissions = sum(p.submission_count for p in problems)
        total_accepted = sum(p.accepted_count for p in problems)

        avg_acceptance_rate = 0.0
        if total_submissions > 0:
            avg_acceptance_rate = (total_accepted / total_submissions) * 100

        difficulty_distribution = {}
        for problem in problems:
            diff = problem.difficulty.value
            difficulty_distribution[diff] = difficulty_distribution.get(diff, 0) + 1

        return {
            "total_problems": total_problems,
            "published_problems": published_problems,
            "total_submissions": total_submissions,
            "total_accepted": total_accepted,
            "average_acceptance_rate": round(avg_acceptance_rate, 2),
            "difficulty_distribution": difficulty_distribution,
        }
