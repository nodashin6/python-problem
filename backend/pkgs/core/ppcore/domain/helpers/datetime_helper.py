"""
DateTime Helper
日時関連ヘルパー
"""

from datetime import UTC, datetime, timezone
from typing import Final

# Constants
DEFAULT_TIMEZONE: Final[timezone] = UTC


class DateTimeHelper:
    """Helper for datetime operations"""

    @staticmethod
    def now() -> datetime:
        """Get current UTC datetime"""
        return datetime.now(DEFAULT_TIMEZONE)

    @staticmethod
    def to_iso_string(dt: datetime) -> str:
        """Convert datetime to ISO string"""
        return dt.isoformat()

    @staticmethod
    def from_iso_string(iso_string: str) -> datetime:
        """Parse ISO string to datetime"""
        return datetime.fromisoformat(iso_string)

    @staticmethod
    def is_recent(dt: datetime, minutes: int = 30) -> bool:
        """Check if datetime is within recent minutes"""
        diff = DateTimeHelper.now() - dt
        return diff.total_seconds() < (minutes * 60)
