"""
Main Application Integration
メインアプリケーション統合 - 全パッケージの協調

各パッケージの責任領域:
- core: 抽象的な設計、汎用的な関数の提供
- auth: user管理
- problem-system: 問題の提供、識別
- judge-system: 提出したコードの実行
- edutorial-system: 問題の解説を管理する
- seed: 指定のリポジトリをcloneすれば、問題集を自作・配布することができる
"""

# Core abstractions
# Domain packages
from auth.ppauth import AuthController, UserController
from core.ppcore import (
    BaseEntity,
    BaseModel,
    CryptographyHelper,
    DateTimeHelper,
    IDomainService,
    IRepository,
    QueueService,
    ValidationHelper,
)
from edutorial_system.ppedut import EditorialDomainService
from judge_system.ppjudg import JudgeQueueService
from problem_system.ppprob import BookController, ProblemController
from seed.ppseed import ImportDomainService

from .app.middleware import setup_middleware

# Application Layer Integration
from .app.routers import api_router
from .queue.dispatcher import QueueDispatcher

__all__ = [
    # Core
    "BaseEntity",
    "BaseModel",
    "IRepository",
    "IDomainService",
    # Controllers
    "UserController",
    "AuthController",
    "ProblemController",
    "BookController",
    # Services
    "JudgeQueueService",
    "EditorialDomainService",
    "ImportDomainService",
    # App components
    "api_router",
    "setup_middleware",
    "QueueDispatcher",
]
