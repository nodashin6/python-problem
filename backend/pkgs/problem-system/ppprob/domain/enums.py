from enum import Enum, StrEnum


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
