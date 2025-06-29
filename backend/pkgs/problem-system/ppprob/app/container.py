"""
Dependency Injection Container
依存性注入コンテナ

Author: Judge System Team
Date: 2025-01-12
"""

import os
from functools import lru_cache

from supabase import Client, create_client

from ..domain.models.domain_config import DomainConfig
from ..domain.repositories.book_repository import BookRepository
from ..domain.repositories.problem_repository import ProblemRepository
from ..infrastructure.supabase.repositories.book_repository_impl import BookRepositoryImpl
from ..infrastructure.supabase.repositories.problem_repository_impl import ProblemRepositoryImpl
from .services import (
    BookApplicationService,
    ProblemApplicationService,
)


class Container:
    """依存性注入コンテナ"""

    def __init__(self):
        self._supabase_client: Client | None = None
        self._domain_config: DomainConfig | None = None
        self._book_repository: BookRepository | None = None
        self._problem_repository: ProblemRepository | None = None
        self._book_service: BookApplicationService | None = None
        self._problem_service: ProblemApplicationService | None = None

    def supabase_client(self) -> Client:
        """Supabaseクライアントを取得"""
        if self._supabase_client is None:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_ANON_KEY")

            if not supabase_url or not supabase_key:
                raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")

            self._supabase_client = create_client(supabase_url, supabase_key)

        return self._supabase_client

    def domain_config(self) -> DomainConfig:
        """ドメイン設定を取得"""
        if self._domain_config is None:
            self._domain_config = DomainConfig(language=os.getenv("DEFAULT_LANGUAGE", "ja"))

        return self._domain_config

    def book_repository(self) -> BookRepository:
        """問題集リポジトリを取得"""
        if self._book_repository is None:
            self._book_repository = BookRepositoryImpl(
                client=self.supabase_client(), config=self.domain_config()
            )

        return self._book_repository

    def problem_repository(self) -> ProblemRepository:
        """問題リポジトリを取得"""
        if self._problem_repository is None:
            self._problem_repository = ProblemRepositoryImpl(
                client=self.supabase_client(), config=self.domain_config()
            )

        return self._problem_repository

    def book_service(self) -> BookApplicationService:
        """問題集アプリケーションサービスを取得"""
        if self._book_service is None:
            self._book_service = BookApplicationService(book_repository=self.book_repository())

        return self._book_service

    def problem_service(self) -> ProblemApplicationService:
        """問題アプリケーションサービスを取得"""
        if self._problem_service is None:
            self._problem_service = ProblemApplicationService(problem_repository=self.problem_repository())

        return self._problem_service


# グローバルコンテナインスタンス
container = Container()
