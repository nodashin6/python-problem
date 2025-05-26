"""
Submission Repository interface
提出リポジトリインターフェース
"""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from ..models import Submission
from ....const import (
    ProgrammingLanguage as Language,
    JudgeResultType as JudgeResult,
    ExecutionStatus,
)


class SubmissionRepository(ABC):
    """提出リポジトリのインターフェース"""

    @abstractmethod
    async def save(self, submission: Submission) -> bool:
        """提出を保存"""
        pass

    @abstractmethod
    async def find_by_id(self, submission_id: uuid.UUID) -> Optional[Submission]:
        """IDで提出を検索"""
        pass

    @abstractmethod
    async def find_by_user(
        self, user_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> List[Submission]:
        """ユーザーIDで提出を検索"""
        pass

    @abstractmethod
    async def find_by_problem(
        self, problem_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> List[Submission]:
        """問題IDで提出を検索"""
        pass

    @abstractmethod
    async def find_by_user_and_problem(
        self, user_id: uuid.UUID, problem_id: uuid.UUID
    ) -> List[Submission]:
        """ユーザーと問題で提出を検索"""
        pass

    @abstractmethod
    async def find_by_status(
        self, status: ExecutionStatus, limit: int = 50
    ) -> List[Submission]:
        """ステータスで提出を検索"""
        pass

    @abstractmethod
    async def find_by_result(
        self, result: JudgeResult, limit: int = 50
    ) -> List[Submission]:
        """結果で提出を検索"""
        pass

    @abstractmethod
    async def find_by_language(
        self, language: Language, limit: int = 50
    ) -> List[Submission]:
        """言語で提出を検索"""
        pass

    @abstractmethod
    async def find_recent(self, limit: int = 50) -> List[Submission]:
        """最近の提出を検索"""
        pass

    @abstractmethod
    async def find_user_best_submissions(
        self, user_id: uuid.UUID, problem_ids: List[uuid.UUID]
    ) -> List[Submission]:
        """ユーザーの最高得点提出を取得"""
        pass

    @abstractmethod
    async def count_by_user(self, user_id: uuid.UUID) -> int:
        """ユーザーの提出数をカウント"""
        pass

    @abstractmethod
    async def count_by_problem(self, problem_id: uuid.UUID) -> int:
        """問題の提出数をカウント"""
        pass

    @abstractmethod
    async def count_by_result(self, result: JudgeResult) -> int:
        """結果別の提出数をカウント"""
        pass

    @abstractmethod
    async def get_user_statistics(self, user_id: uuid.UUID) -> dict:
        """ユーザーの統計情報を取得"""
        pass

    @abstractmethod
    async def get_problem_statistics(self, problem_id: uuid.UUID) -> dict:
        """問題の統計情報を取得"""
        pass

    @abstractmethod
    async def delete(self, submission_id: uuid.UUID) -> bool:
        """提出を削除"""
        pass
