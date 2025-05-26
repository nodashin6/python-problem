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

import redis.asyncio as redis
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


class RedisCache(CacheBackend):
    """Redis キャッシュ実装"""

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or settings.redis_url or "redis://localhost:6379/0"
        self.client: Optional[redis.Redis] = None

    async def initialize(self):
        """Redis接続を初期化"""
        try:
            self.client = redis.from_url(self.redis_url, decode_responses=True)
            await self.client.ping()
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.warning(
                f"Failed to initialize Redis cache: {e}. Falling back to memory cache."
            )
            raise

    async def close(self):
        """Redis接続を閉じる"""
        if self.client:
            await self.client.close()

    def _serialize(self, value: Any) -> str:
        """値をシリアライズ"""
        if isinstance(value, (str, int, float)):
            return json.dumps({"type": "simple", "value": value})
        else:
            return json.dumps({"type": "complex", "value": pickle.dumps(value).hex()})

    def _deserialize(self, data: str) -> Any:
        """値をデシリアライズ"""
        try:
            obj = json.loads(data)
            if obj["type"] == "simple":
                return obj["value"]
            else:
                return pickle.loads(bytes.fromhex(obj["value"]))
        except Exception:
            return data

    async def get(self, key: str) -> Optional[Any]:
        if not self.client:
            return None

        try:
            data = await self.client.get(key)
            return self._deserialize(data) if data else None
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        if not self.client:
            return False

        try:
            serialized = self._serialize(value)
            ttl = ttl or CACHE_TTL_SECONDS
            await self.client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        if not self.client:
            return False

        try:
            result = await self.client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis delete error for key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        if not self.client:
            return False

        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis exists error for key {key}: {e}")
            return False

    async def clear(self) -> bool:
        if not self.client:
            return False

        try:
            await self.client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
            return False


class CacheManager:
    """統合キャッシュマネージャー"""

    def __init__(self):
        self.backend: Optional[CacheBackend] = None
        self._fallback_backend: MemoryCache = MemoryCache()

    async def initialize(self, use_redis: bool = True):
        """キャッシュバックエンドを初期化"""
        if use_redis and settings.redis_url:
            try:
                redis_cache = RedisCache()
                await redis_cache.initialize()
                self.backend = redis_cache
                logger.info("Using Redis cache backend")
            except Exception:
                logger.warning("Failed to initialize Redis, using memory cache")
                self.backend = self._fallback_backend
        else:
            self.backend = self._fallback_backend
            logger.info("Using memory cache backend")

    async def close(self):
        """キャッシュバックエンドを閉じる"""
        if isinstance(self.backend, RedisCache):
            await self.backend.close()

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
