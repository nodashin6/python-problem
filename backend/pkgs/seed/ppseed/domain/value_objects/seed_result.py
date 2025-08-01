"""
Seed Result Value Objects
シード結果値オブジェクト
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class SeedResult:
    """シード処理の結果を表す値オブジェクト"""
    
    entity_type: str
    total_processed: int
    created_count: int
    updated_count: int
    skipped_count: int
    errors: List[str]
    success: bool
    
    @property
    def is_successful(self) -> bool:
        """処理が成功したかどうか"""
        return self.success and len(self.errors) == 0
    
    @property
    def success_rate(self) -> float:
        """成功率を計算"""
        if self.total_processed == 0:
            return 1.0
        return (self.created_count + self.updated_count) / self.total_processed


@dataclass(frozen=True)
class SeedStatistics:
    """シードデータの統計情報を表す値オブジェクト"""
    
    books_total: int
    books_by_difficulty: Dict[str, int]
    problems_total: int
    problems_by_difficulty: Dict[str, int]
    problems_by_status: Dict[str, int]
    success: bool
    error: Optional[str] = None
    
    @property
    def is_valid(self) -> bool:
        """統計情報が有効かどうか"""
        return self.success and self.error is None


@dataclass(frozen=True)
class TestCaseFileResult:
    """テストケースファイル作成結果を表す値オブジェクト"""
    
    total_files: int
    created_files: List[str]
    errors: List[str]
    success: bool
    base_directory: Optional[str] = None
    
    @property
    def created_count(self) -> int:
        """作成されたファイル数"""
        return len(self.created_files)
    
    @property
    def is_successful(self) -> bool:
        """処理が成功したかどうか"""
        return self.success and len(self.errors) == 0