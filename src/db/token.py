from abc import ABC, abstractmethod

import backoff
from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError

from core.config import redis_settings


class TokenDBBase(ABC):

    @abstractmethod
    async def put(self, token: str, user_id: str, expire_in_sec: int) -> None:
        """Add token to token db"""
        pass

    @abstractmethod
    async def is_exist(self, token: str) -> bool:
        """Check token is exists"""
        pass


class TokenDB(TokenDBBase):
    def __init__(self, host: str, port: int, password: str) -> None:
        self.redis = Redis(host=host, port=port, password=password)

    @backoff.on_exception(backoff.expo,
                          (RedisConnectionError),
                          max_tries=5,
                          raise_on_giveup=True,
                          )
    async def put(self, token: str, user_id: str, expire_in_sec: int) -> None:
        print(token, user_id, expire_in_sec)
        await self.redis.set(token, user_id, expire_in_sec)

    @backoff.on_exception(backoff.expo,
                          (RedisConnectionError),
                          max_tries=5,
                          raise_on_giveup=True,
                          )
    async def is_exist(self, token: str) -> bool:
        is_exist = await self.redis.exists(token)
        return is_exist


@backoff.on_exception(backoff.expo,
                      (RedisConnectionError),
                      max_tries=5,
                      raise_on_giveup=True,
                      )
async def get_token_db() -> TokenDBBase:
    return TokenDB(redis_settings.host, redis_settings.port, redis_settings.password.get_secret_value())
