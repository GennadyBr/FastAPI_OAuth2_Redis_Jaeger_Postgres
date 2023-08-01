from logging import config as logging_config
from pathlib import Path

from pydantic import BaseSettings

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)


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