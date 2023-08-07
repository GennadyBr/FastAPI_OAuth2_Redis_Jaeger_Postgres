from sqlalchemy import update, and_, select
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseSettings, AnyUrl

from uuid import UUID
from typing import Union

from src.db.models import Entry
from src.crud.base_classes import CrudBase
from src.crud.entry import EntryDAL
# from src.db.session import get_db

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from logging import config as logging_config
from pathlib import Path

from pydantic import BaseSettings, AnyUrl



class UserDBSettings(BaseSettings):
    name: str = 'postgres'
    user: str = 'postgres'
    password: str = 'postgres'
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
        env_prefix = 'auth_'


class RedisSettings(BaseSettings):
    host: str = 'redis'
    port: int = 6379
    access_token_expire_sec: int = 60 * 5  # 5 минут
    refresh_token_expire_sec: int = 60 * 60  # 60 минут

    class Config:
        env_prefix = 'redis_'


auth_settings = AuthSettings()
redis_settings = RedisSettings()
user_db_settings = UserDBSettings()

#############################################
# BLOCK FOR COMMON INTERATION WITH DATABASE #
#############################################

# create async engine for interaction with database
engine = create_async_engine(user_db_settings.async_url, future=True, echo=True)

# create session for interaction with database
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncGenerator:
    """Dependency for getting async session"""
    try:
        session: AsyncSession = async_session()
        yield session
    finally:
        await session.close()

async def test(uuid):
    db: AsyncSession = Depends(get_db)
    async with db as session:
        async with session.begin():
            entry_dal = EntryDAL(session)
            entry = await entry_dal.get_by_user_id(uuid)
    return entry

print(test({"user_id":'22c65bb8-4944-4d22-9a4a-cf30e1fa7341'}))
