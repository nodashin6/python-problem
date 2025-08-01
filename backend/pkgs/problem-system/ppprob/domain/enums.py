from enum import Enum, StrEnum


class DifficultyLevel(StrEnum):
    """難易度レベル"""
    
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ProblemStatus(StrEnum):
    """問題ステータス"""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"


class Language(StrEnum):
    """対応言語"""

    JAPANESE = "ja"
    ENGLISH = "en"
