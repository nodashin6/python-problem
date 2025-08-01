"""
Problem Content Validator
問題コンテンツバリデーター

Author: Judge System Team
Date: 2025-06-30
"""

import re
from typing import Any


class ProblemContentValidator:
    """Validator for problem content"""

    @staticmethod
    def validate_markdown_content(content: str) -> dict[str, Any]:
        """
        Validate markdown content for problems

        Returns validation result with any issues found
        """
        issues = []

        # Check for empty content
        if not content.strip():
            issues.append("Content cannot be empty")

        # Check for basic markdown structure
        if not re.search(r"#+\s+", content):
            issues.append("Content should contain at least one heading")

        # Check for code blocks (problems should have examples)
        if not re.search(r"```[\s\S]*?```", content):
            issues.append("Content should contain code examples in code blocks")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "content_length": len(content),
        }

    @staticmethod
    def validate_problem_title(title: str) -> dict[str, Any]:
        """Validate problem title"""
        issues = []

        if not title.strip():
            issues.append("Title cannot be empty")

        if len(title) > 200:
            issues.append("Title is too long (max 200 characters)")

        if len(title) < 5:
            issues.append("Title is too short (min 5 characters)")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
        }

    @staticmethod
    def validate_tags(tags: list[str]) -> dict[str, Any]:
        """Validate problem tags"""
        issues = []

        if len(tags) > 10:
            issues.append("Too many tags (max 10)")

        for tag in tags:
            if not tag.strip():
                issues.append("Tags cannot be empty")
                break

            if len(tag) > 50:
                issues.append(f"Tag '{tag}' is too long (max 50 characters)")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
        }
