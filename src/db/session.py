from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from core.config import user_db_settings

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
