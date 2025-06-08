"""
Core Domain API Middleware
コアドメインAPIミドルウェア

Author: Judge System Team
Date: 2025-01-12
"""

import time
from typing import Callable
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class CoreDomainMiddleware(BaseHTTPMiddleware):
    """コアドメイン固有のミドルウェア"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """リクエスト処理"""
        start_time = time.time()

        # リクエストログ
        logger.info(f"Core domain request: {request.method} {request.url.path}")

        try:
            response = await call_next(request)

            # レスポンス時間計測
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Domain"] = "core"

            logger.info(f"Core domain response: {response.status_code} in {process_time:.3f}s")

            return response

        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"Core domain error: {str(e)} in {process_time:.3f}s")
            raise


class CoreCacheMiddleware(BaseHTTPMiddleware):
    """コアドメイン用キャッシュミドルウェア"""

    def __init__(self, app, cache_time: int = 300):
        super().__init__(app)
        self.cache_time = cache_time
        self.cache = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """キャッシュ可能なリクエストをキャッシュ"""

        # GETリクエストのみキャッシュ対象
        if request.method != "GET":
            return await call_next(request)

        # キャッシュキーの生成
        cache_key = f"{request.url.path}?{request.url.query}"

        # キャッシュから取得
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if time.time() - cached_data["timestamp"] < self.cache_time:
                logger.info(f"Cache hit for {cache_key}")
                response = Response(
                    content=cached_data["content"],
                    status_code=cached_data["status_code"],
                    headers=cached_data["headers"],
                )
                response.headers["X-Cache"] = "HIT"
                return response

        # キャッシュミス - リクエスト実行
        response = await call_next(request)

        # 成功レスポンスをキャッシュ
        if response.status_code == 200:
            self.cache[cache_key] = {
                "content": response.body,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "timestamp": time.time(),
            }
            response.headers["X-Cache"] = "MISS"
            logger.info(f"Cached response for {cache_key}")

        return response


def setup_core_middleware(app):
    """コアドメイン用ミドルウェアを設定"""

    # キャッシュミドルウェア (5分間キャッシュ)
    app.add_middleware(CoreCacheMiddleware, cache_time=300)

    # コアドメイン固有のミドルウェア
    app.add_middleware(CoreDomainMiddleware)

    logger.info("Core domain middleware configured")
