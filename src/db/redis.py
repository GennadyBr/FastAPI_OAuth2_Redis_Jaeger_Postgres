from typing import Any, Optional

import backoff
from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError

from core.config import redis_settings
from db.abstract import AbstractCache

redis: Optional[Redis] = None


class RedisCache(AbstractCache):

    def __init__(self, redis_host: str, redis_port: int):
        self.redis = Redis(host=redis_host, port=redis_port)

    @backoff.on_exception(backoff.expo, RedisConnectionError, max_tries=2, raise_on_giveup=False)
    async def put_to_cache(self, key: str, value: Any, expire_in_sec: int):
        await self.redis.set(key, value, expire_in_sec)

    @backoff.on_exception(backoff.expo, RedisConnectionError, max_tries=2, raise_on_giveup=False)
    async def get_from_cache_by_key(self, key: str):
        data = await self.redis.get(key)
        return data


# Функция понадобится при внедрении зависимостей
@backoff.on_exception(backoff.expo, RedisConnectionError, max_tries=2, raise_on_giveup=False)
async def get_cache() -> RedisCache:
    cache = RedisCache(redis_settings.host, redis_settings.port)
    return cache
