from logging import config as logging_config
from pathlib import Path

from pydantic import BaseSettings
from envparse import Env
import os
from dotenv import load_dotenv

load_dotenv()

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)

def user_db_settings():
    pass

env = Env()

REAL_DATABASE_URL = env.str(
    "REAL_DATABASE_URL",
    default=f'postgresql+asyncpg://{os.getenv("PG_LOGIN")}:{os.getenv("PG_PWD")}@0.0.0.0:5432/postgres'
) #connect string to database
# postgresql+asyncpg - это драйвер подключения что бы алхимия синхронного подключалась
# postgres:postgres - это логин и пароль


class UserDBSettings(BaseSettings):
    SQLALCHEMY_DATABASE_URL = f'postgresql://{os.getenv("PG_LOGIN")}:{os.getenv("PG_PWD")}@0.0.0.0:5432/postgres'



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