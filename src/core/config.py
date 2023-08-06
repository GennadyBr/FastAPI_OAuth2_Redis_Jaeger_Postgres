from logging import config as logging_config
from pathlib import Path

from pydantic import BaseSettings, AnyUrl

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class UserDBSettings(BaseSettings):
    name: str
    user: str
    password: str
    port: int = 5432
    service_name: str = 'db_users'

    class Config:
        env_prefix = 'pg_db_'

    def _url(cls, asyncpg: bool = False) -> AnyUrl:
        return f'postgresql{"+asyncpg" * asyncpg}://{cls.user}:{cls.password}@{cls.service_name}:{cls.port}/{cls.name}'
    
    @property
    def url(cls) -> AnyUrl:
        return cls._url()

    @property
    def async_url(cls) -> AnyUrl:
        return cls._url(asyncpg=True)



class AuthSettings(BaseSettings):
    project_name: str = 'Auth service'
    base_dir: Path = Path(__file__).resolve(strict=True).parent.parent
    log_lvl: str = 'DEBUG'

    class Config:
        env_prefix = 'auth'


class RedisSettings(BaseSettings):
    host: str = "redis"
    # ??? 6379
    port: int = 6380
    access_token_expire_sec: int = 60 * 5  # 5 минут
    refresh_token_expire_sec: int = 60 * 60  # 60 минут

    class Config:
        env_prefix = 'redis_'


auth_settings = AuthSettings()
redis_settings = RedisSettings()
user_db_settings = UserDBSettings()