from datetime import datetime

from pydantic import UUID4, Field, field_validator
from pydddi import IEntity


class UserStatusEntity(IEntity):
    """
    Represents a user's problem solving status.
    This class contains fields that represent the user's progress on a specific problem.
    """

    id: UUID4
    user_id: UUID4
    problem_id: UUID4
    is_solved: bool = Field(default=False)
    attempts: int = Field(default=0)
    best_submission_time: int | None = Field(
        default=None, description="Best submission time in milliseconds"
    )
    first_solved_at: datetime | None = None
    last_attempt_at: datetime | None = None
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)

    @field_validator("attempts")
    def validate_attempts(cls, value: int) -> int:
        if value < 0:
            raise ValueError("Attempts cannot be negative")
        return value

    @field_validator("best_submission_time")
    def validate_best_submission_time(cls, value: int | None) -> int | None:
        if value is not None and value <= 0:
            raise ValueError("Submission time must be positive")
        return value

    def mark_as_solved(self, submission_time: int | None = None) -> None:
        """Mark the problem as solved"""
        self.is_solved = True
        if submission_time is not None:
            if self.best_submission_time is None or submission_time < self.best_submission_time:
                self.best_submission_time = submission_time
        if self.first_solved_at is None:
            self.first_solved_at = datetime.utcnow()
        self.last_attempt_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def record_attempt(self) -> None:
        """Record a new attempt"""
        self.attempts += 1
        self.last_attempt_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
