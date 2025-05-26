"""
Code Execution Repository interface
コード実行リポジトリインターフェース
"""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from ..models import CodeExecution
from ....const import Language, ExecutionStatus


class CodeExecutionRepository(ABC):
    """コード実行リポジトリのインターフェース"""

    @abstractmethod
    async def save(self, execution: CodeExecution) -> bool:
        """コード実行を保存"""
        pass

    @abstractmethod
    async def find_by_id(self, execution_id: uuid.UUID) -> Optional[CodeExecution]:
        """IDでコード実行を検索"""
        pass

    @abstractmethod
    async def find_by_status(
        self, status: ExecutionStatus, limit: int = 50
    ) -> List[CodeExecution]:
        """ステータスでコード実行を検索"""
        pass

    @abstractmethod
    async def find_by_language(
        self, language: Language, limit: int = 50
    ) -> List[CodeExecution]:
        """言語でコード実行を検索"""
        pass

    @abstractmethod
    async def find_recent(self, limit: int = 50) -> List[CodeExecution]:
        """最近のコード実行を検索"""
        pass

    @abstractmethod
    async def find_pending(self, limit: int = 50) -> List[CodeExecution]:
        """実行待ちのコード実行を検索"""
        pass

    @abstractmethod
    async def find_by_date_range(
        self, start_date: datetime, end_date: datetime, limit: int = 100
    ) -> List[CodeExecution]:
        """日付範囲でコード実行を検索"""
        pass

    @abstractmethod
    async def count_by_status(self, status: ExecutionStatus) -> int:
        """ステータス別のコード実行数をカウント"""
        pass

    @abstractmethod
    async def count_by_language(self, language: Language) -> int:
        """言語別のコード実行数をカウント"""
        pass

    @abstractmethod
    async def get_execution_statistics(
        self, start_date: datetime, end_date: datetime
    ) -> dict:
        """実行統計を取得"""
        pass

    @abstractmethod
    async def delete(self, execution_id: uuid.UUID) -> bool:
        """コード実行を削除"""
        pass

    @abstractmethod
    async def delete_old_executions(self, before_date: datetime) -> int:
        """古いコード実行を削除"""
        pass
