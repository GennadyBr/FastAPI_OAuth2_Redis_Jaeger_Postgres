from logging import config as logging_config
from pathlib import Path

from pydantic import BaseSettings, AnyUrl, Field, SecretStr

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class APPSettings(BaseSettings):
    project_name: str = 'Movies API'
    # base_dir: Path = Path(__file__).resolve(strict=True).parent.parent
    log_lvl: str = 'DEBUG'

class UserDBSettings(BaseSettings):
    name: str
    user: str
    password: SecretStr
    port: int = 5432
    service_name: str = '0.0.0.0'

    class Config:
        env_prefix = 'pg_db_'

    def _url(cls, asyncpg: bool = False) -> AnyUrl:
        return f'postgresql{"+asyncpg" * asyncpg}://{cls.user}:{cls.password.get_secret_value()}@{cls.service_name}:{cls.port}/{cls.name}'

    @property
    def url(cls) -> AnyUrl:
        return cls._url()

    @property
    def async_url(cls) -> AnyUrl:
        return cls._url(asyncpg=True)

class TokenSettings(BaseSettings):
    access_expire: int = 10 # min
    access_secret_key: SecretStr = ''
    refresh_expire: int = 60 # min
    refresh_secret_key: SecretStr = ''
    refresh_token_cookie_name: str = 'refresh_token'
    algorithm: str = 'HS256'

    class Config:
        env_prefix = 'token_'

class RedisSettings(BaseSettings):
    host: str = 'redis_token'
    port: int = 6379
    password: SecretStr = ''

    class Config:
        env_prefix = 'redis_'

app_settings = APPSettings()
token_settings = TokenSettings()
redis_settings = RedisSettings()
user_db_settings = UserDBSettings()
