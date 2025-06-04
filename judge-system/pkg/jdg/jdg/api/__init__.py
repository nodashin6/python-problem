"""
Judge Domain API Layer
ジャッジドメインAPI層

このモジュールはジャッジドメインのWeb API層を提供します。
FastAPIを使用してRESTful APIを実装しています。
"""

from .routes import judge_router
from .middleware import setup_middleware

__all__ = [
    "judge_router",
    "setup_middleware",
]
