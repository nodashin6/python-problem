"""
Cache infrastructure components
キャッシュインフラストラクチャ
"""

import json
import logging
import pickle
from abc import ABC, abstractmethod
from typing import Any, Optional, Union, Dict, List
from datetime import datetime, timedelta
import asyncio
import hashlib

# import redis.asyncio as redis  # 一時的に無効化 - 後でSupabaseベースの実装に置き換え
from ..env import settings
from ..const import CACHE_TTL_SECONDS, CACHE_MAX_SIZE

logger = logging.getLogger(__name__)


class CacheBackend(ABC):
    """キャッシュバックエンドの抽象化"""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """値を取得"""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """値を設定"""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """値を削除"""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """キーが存在するかチェック"""
        pass

    @abstractmethod
    async def clear(self) -> bool:
        """全てのキーを削除"""
        pass


class MemoryCache(CacheBackend):
    """メモリキャッシュ実装"""

    def __init__(
        self, max_size: int = CACHE_MAX_SIZE, default_ttl: int = CACHE_TTL_SECONDS
    ):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            if key not in self.cache:
                return None

            item = self.cache[key]

            # TTLチェック
            if item["expires_at"] and datetime.now() > item["expires_at"]:
                del self.cache[key]
                return None

            return item["value"]

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        async with self._lock:
            # キャッシュサイズ制限
            if len(self.cache) >= self.max_size and key not in self.cache:
                # LRU: 最も古いアイテムを削除
                oldest_key = min(
                    self.cache.keys(), key=lambda k: self.cache[k]["created_at"]
                )
                del self.cache[oldest_key]

            ttl = ttl or self.default_ttl
            expires_at = datetime.now() + timedelta(seconds=ttl) if ttl > 0 else None

            self.cache[key] = {
                "value": value,
                "created_at": datetime.now(),
                "expires_at": expires_at,
            }
            return True

    async def delete(self, key: str) -> bool:
        async with self._lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False

    async def exists(self, key: str) -> bool:
        return await self.get(key) is not None

    async def clear(self) -> bool:
        async with self._lock:
            self.cache.clear()
            return True


"""
# RedisCache class temporarily disabled - will be replaced with Supabase-based implementation
class RedisCache(CacheBackend):
    # Redis キャッシュ実装 - 一時的に無効化
    pass
"""


class CacheManager:
    """統合キャッシュマネージャー"""

    def __init__(self):
        self.backend: Optional[CacheBackend] = None
        self._fallback_backend: MemoryCache = MemoryCache()

    async def initialize(self, use_redis: bool = False):  # 一時的にRedisを無効化
        """キャッシュバックエンドを初期化"""
        # Redis機能を一時的に無効化 - 将来的にSupabaseベースの実装に置き換え
        self.backend = self._fallback_backend
        logger.info("Using memory cache backend (Redis temporarily disabled)")

    async def close(self):
        """キャッシュバックエンドを閉じる"""
        # Redis関連の処理を一時的に無効化
        pass

    def _generate_key(self, namespace: str, key: str, **kwargs) -> str:
        """キャッシュキーを生成"""
        key_parts = [namespace, key]

        if kwargs:
            # パラメータをソートして一意なキーを生成
            sorted_params = sorted(kwargs.items())
            param_str = "&".join(f"{k}={v}" for k, v in sorted_params)
            key_parts.append(hashlib.md5(param_str.encode()).hexdigest()[:8])

        return ":".join(key_parts)

    async def get(self, namespace: str, key: str, **kwargs) -> Optional[Any]:
        """値を取得"""
        if not self.backend:
            return None

        cache_key = self._generate_key(namespace, key, **kwargs)
        return await self.backend.get(cache_key)

    async def set(
        self, namespace: str, key: str, value: Any, ttl: Optional[int] = None, **kwargs
    ) -> bool:
        """値を設定"""
        if not self.backend:
            return False

        cache_key = self._generate_key(namespace, key, **kwargs)
        return await self.backend.set(cache_key, value, ttl)

    async def delete(self, namespace: str, key: str, **kwargs) -> bool:
        """値を削除"""
        if not self.backend:
            return False

        cache_key = self._generate_key(namespace, key, **kwargs)
        return await self.backend.delete(cache_key)

    async def exists(self, namespace: str, key: str, **kwargs) -> bool:
        """キーが存在するかチェック"""
        if not self.backend:
            return False

        cache_key = self._generate_key(namespace, key, **kwargs)
        return await self.backend.exists(cache_key)

    async def clear_namespace(self, namespace: str) -> bool:
        """名前空間のキャッシュをクリア"""
        # Redis の場合はパターンマッチングで削除
        # メモリキャッシュの場合は全てのキーをチェック
        if isinstance(self.backend, RedisCache) and self.backend.client:
            try:
                pattern = f"{namespace}:*"
                keys = await self.backend.client.keys(pattern)
                if keys:
                    await self.backend.client.delete(*keys)
                return True
            except Exception as e:
                logger.error(f"Failed to clear namespace {namespace}: {e}")
                return False
        elif isinstance(self.backend, MemoryCache):
            async with self.backend._lock:
                keys_to_delete = [
                    k
                    for k in self.backend.cache.keys()
                    if k.startswith(f"{namespace}:")
                ]
                for key in keys_to_delete:
                    del self.backend.cache[key]
                return True

        return False


# デコレータ関数
def cached(
    namespace: str, ttl: Optional[int] = None, key_func: Optional[callable] = None
):
    """キャッシュデコレータ"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # キー生成
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"

            # キャッシュから取得を試行
            cached_result = await cache_manager.get(namespace, cache_key)
            if cached_result is not None:
                return cached_result

            # 関数を実行
            result = await func(*args, **kwargs)

            # 結果をキャッシュ
            await cache_manager.set(namespace, cache_key, result, ttl)

            return result

        return wrapper

    return decorator


# グローバルインスタンス
cache_manager = CacheManager()


async def initialize_cache():
    """キャッシュを初期化"""
    await cache_manager.initialize()


async def close_cache():
    """キャッシュを閉じる"""
    await cache_manager.close()
