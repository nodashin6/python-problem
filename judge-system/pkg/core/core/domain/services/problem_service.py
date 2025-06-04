"""
Problem domain service
"""

from typing import List, Optional, Dict, Any
from uuid import UUID

from ..models import Problem, JudgeCase, Tag, ProblemMetadata, ProblemContent
from ..repositories import (
    ProblemRepository,
    JudgeCaseRepository,
    ProblemContentRepository,
)
from ....const import DifficultyLevel, ProblemStatus, JudgeCaseType, Language
from ....shared.events import EventBus


class ProblemDomainService:
    """Problem domain service for problem-related business logic"""

    def __init__(
        self,
        problem_repo: ProblemRepository,
        judge_case_repo: JudgeCaseRepository,
        content_repo: ProblemContentRepository,
        event_bus: EventBus,
    ):
        self.problem_repo = problem_repo
        self.judge_case_repo = judge_case_repo
        self.content_repo = content_repo
        self.event_bus = event_bus

    async def create_problem(
        self,
        title: str,
        description: str,
        author_id: UUID,
        difficulty: DifficultyLevel = DifficultyLevel.EASY,
        tags: List[str] = None,
        metadata: ProblemMetadata = None,
        book_id: Optional[UUID] = None,
    ) -> Problem:
        """Create a new problem"""
        # Check for duplicate title
        existing = await self.problem_repo.find_by_title(title)
        if existing:
            raise ValueError("Problem with this title already exists")

        # Convert tags to Tag objects
        tag_objects = {Tag(name=tag) for tag in (tags or [])}

        # Create problem entity
        problem = Problem(
            title=title,
            description=description,
            author_id=author_id,
            difficulty=difficulty,
            tags=tag_objects,
            metadata=metadata or ProblemMetadata(),
            book_id=book_id,
        )

        # Save problem
        created_problem = await self.problem_repo.create(problem)

        # Publish domain events
        for event in created_problem.clear_events():
            await self.event_bus.publish(event)

        return created_problem

    async def add_judge_case(
        self,
        problem_id: UUID,
        name: str,
        input_data: str,
        expected_output: str,
        case_type: JudgeCaseType = JudgeCaseType.HIDDEN,
        points: int = 1,
    ) -> JudgeCase:
        """Add a judge case to a problem"""
        # Verify problem exists
        problem = await self.problem_repo.get(problem_id)
        if not problem:
            raise ValueError("Problem not found")

        # Get next display order
        existing_cases = await self.judge_case_repo.find_by_problem(problem_id)
        display_order = len(existing_cases)

        # Create judge case
        judge_case = JudgeCase(
            problem_id=problem_id,
            name=name,
            input_data=input_data,
            expected_output=expected_output,
            case_type=case_type,
            display_order=display_order,
            points=points,
        )

        # Save judge case
        created_case = await self.judge_case_repo.create(judge_case)

        # Publish domain events
        for event in created_case.clear_events():
            await self.event_bus.publish(event)

        return created_case

    async def add_problem_content(
        self,
        problem_id: UUID,
        language: str,
        title: str,
        description: str,
        input_format: str = "",
        output_format: str = "",
        constraints: str = "",
        sample_explanation: str = "",
    ) -> ProblemContent:
        """Add localized content for a problem"""
        # Verify problem exists
        problem = await self.problem_repo.get(problem_id)
        if not problem:
            raise ValueError("Problem not found")

        # Check if content already exists for this language
        existing = await self.content_repo.find_by_problem_and_language(
            problem_id, language
        )
        if existing:
            raise ValueError(f"Content already exists for language: {language}")

        # Create content
        content = ProblemContent(
            problem_id=problem_id,
            language=language,
            title=title,
            description=description,
            input_format=input_format,
            output_format=output_format,
            constraints=constraints,
            sample_explanation=sample_explanation,
        )

        return await self.content_repo.create(content)

    async def publish_problem(self, problem_id: UUID, publisher_id: UUID) -> bool:
        """Publish a problem"""
        problem = await self.problem_repo.get(problem_id)
        if not problem:
            return False

        # Validate problem has required test cases
        judge_cases = await self.judge_case_repo.find_by_problem(problem_id)
        if not judge_cases:
            raise ValueError("Problem must have at least one test case")

        # Check for sample cases
        sample_cases = await self.judge_case_repo.find_sample_cases(problem_id)
        if not sample_cases:
            raise ValueError("Problem must have at least one sample test case")

        # Publish problem
        problem.publish()
        await self.problem_repo.update(problem_id, problem)

        # Publish domain events
        for event in problem.clear_events():
            await self.event_bus.publish(event)

        return True

    async def update_problem_statistics(self, problem_id: UUID) -> Dict[str, Any]:
        """Update and return problem statistics"""
        # This would typically be called from the judge domain
        # when submissions are processed
        stats = await self.problem_repo.get_statistics(problem_id)

        problem = await self.problem_repo.get(problem_id)
        if problem:
            problem.update_statistics(
                stats.get("submission_count", 0), stats.get("accepted_count", 0)
            )
            await self.problem_repo.update(problem_id, problem)

        return stats

    async def calculate_difficulty_score(self, problem_id: UUID) -> float:
        """Calculate dynamic difficulty score based on statistics"""
        stats = await self.problem_repo.get_statistics(problem_id)

        submission_count = stats.get("submission_count", 0)
        acceptance_rate = stats.get("acceptance_rate", 0.0)

        if submission_count < 10:
            # Not enough data
            return 0.0

        # Simple difficulty calculation (can be enhanced)
        if acceptance_rate > 80:
            return 1.0  # Easy
        elif acceptance_rate > 60:
            return 2.0  # Medium
        elif acceptance_rate > 40:
            return 3.0  # Hard
        elif acceptance_rate > 20:
            return 4.0  # Very Hard
        else:
            return 5.0  # Extremely Hard

    async def get_problem_recommendations(
        self, user_id: UUID, limit: int = 10
    ) -> List[Problem]:
        """Get problem recommendations for a user"""
        # This would be enhanced with user solving history and preferences
        # For now, return published problems
        return await self.problem_repo.find_published(limit=limit)

    async def validate_judge_cases(self, problem_id: UUID) -> Dict[str, Any]:
        """Validate judge cases for a problem"""
        judge_cases = await self.judge_case_repo.find_by_problem(problem_id)

        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "sample_count": 0,
            "hidden_count": 0,
            "total_points": 0,
        }

        sample_count = 0
        hidden_count = 0
        total_points = 0

        for case in judge_cases:
            if case.case_type == JudgeCaseType.SAMPLE:
                sample_count += 1
            elif case.case_type == JudgeCaseType.HIDDEN:
                hidden_count += 1

            total_points += case.points

            # Basic validation
            if not case.input_data.strip():
                validation_result["errors"].append(
                    f"Judge case '{case.name}' has empty input"
                )
                validation_result["valid"] = False

            if not case.expected_output.strip():
                validation_result["errors"].append(
                    f"Test case '{case.name}' has empty output"
                )
                validation_result["valid"] = False

        validation_result["sample_count"] = sample_count
        validation_result["hidden_count"] = hidden_count
        validation_result["total_points"] = total_points

        # Validation rules
        if sample_count == 0:
            validation_result["errors"].append(
                "Problem must have at least one sample test case"
            )
            validation_result["valid"] = False

        if hidden_count == 0:
            validation_result["warnings"].append(
                "Problem should have hidden test cases"
            )

        if total_points == 0:
            validation_result["errors"].append(
                "Problem must have test cases with points"
            )
            validation_result["valid"] = False

        return validation_result
