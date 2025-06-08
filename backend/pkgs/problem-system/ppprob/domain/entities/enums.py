from enum import Enum


class ProblemStatus(str, Enum):
    """問題ステータス"""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"


class Language(str, Enum):
    """対応言語"""

    JAPANESE = "ja"
    ENGLISH = "en"
