from uuid import UUID
from typing import Union, Optional, List

from sqlalchemy import update, tuple_, select
from sqlalchemy.ext.asyncio import AsyncSession

import logging.config
from core.logger import LOGGING

logging.config.dictConfig(LOGGING)
log = logging.getLogger(__name__)

from db.models import Entry
from crud.base_classes import CrudBase


###########################################################
# BLOCK FOR INTERACTION WITH DATABASE IN BUSINESS CONTEXT #
###########################################################

class EntryDAL(CrudBase):
    """Data Access Layer for operation CRUD"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, user_id: UUID, user_agent: str, refresh_token: str) -> Union[Entry, Exception]:
        """Create Entry"""
        try:
            new_entry = Entry(
                user_id=user_id,
                user_agent=user_agent,
                refresh_token=refresh_token,
            )
            self.db_session.add(new_entry)
            await self.db_session.commit()
            return new_entry
        except Exception as err:
            log.error("Ошибка: ", err)
            log.error("Тип ошибки: ", type(err))
            return err

    async def delete(self, id: Union[str, UUID]) -> Union[UUID, None, Exception]:
        try:
            query = update(Entry). \
                where(Entry.uuid == id). \
                values(is_active=False).returning(Entry.uuid)
            res = await self.db_session.execute(query)
            await self.db_session.commit()
            deleted_entry_id_row = res.fetchone()
            if deleted_entry_id_row is not None:
                return deleted_entry_id_row[0]
        except Exception as err:
            log.error("Ошибка: ", err)
            log.error("Тип ошибки: ", type(err))
            return err

    async def get(self, id: UUID) -> Union[Entry, None, Exception]:
        try:
            query = select(Entry).where(Entry.uuid == id)
            res = await self.db_session.execute(query)
            entry_row = res.fetchone()
            if entry_row is not None:
                return entry_row[0]
        except Exception as err:
            log.error("Ошибка: ", err)
            log.error("Тип ошибки: ", type(err))
            return err

    async def update(self, id: UUID, **kwargs) -> Union[UUID, None, Exception]:
        try:
            query = update(Entry). \
                where(Entry.uuid == id). \
                values(kwargs). \
                returning(Entry.uuid)
            res = await self.db_session.execute(query)
            await self.db_session.commit()
            update_entry_id_row = res.fetchone()
            if update_entry_id_row is not None:
                return update_entry_id_row[0]
        except Exception as err:
            log.error("Ошибка: ", err)
            log.error("Тип ошибки: ", type(err))
            return err

    async def get_by_user_id(self,
                             user_id: UUID,
                             unique: bool = False,
                             only_active: bool = False,
                             page_size: int = None, 
                             page_number: int = None,
                             ) -> Optional[Union[List[Entry], None, Exception]]:
        try:
            query = select(Entry).where(Entry.user_id == user_id)
            if only_active:
                query = query.where(Entry.is_active == True)
            if unique:
                query = query.distinct(tuple_(Entry.user_agent, Entry.is_active))
            if page_size:
                query = query.limit(page_size)
            if page_number: 
                query = query.offset(page_number*page_size - page_size)
            res = await self.db_session.execute(query)
            entries = res.scalars().fetchall()
            return entries
        except Exception as err:
            log.error("Ошибка: ", err)
            log.error("Тип ошибки: ", type(err))
            return err

    async def get_by_user_agent(self,
                                user_agent: str,
                                only_active: bool = False) -> Optional[Union[Entry, None, Exception]]:
        try:
            query = select(Entry).where(Entry.user_agent == user_agent)
            if only_active:
                query = query.where(Entry.is_active == True)
            res = await self.db_session.execute(query)
            entry_row = res.fetchone()
            if entry_row is not None:
                return entry_row[0]
        except Exception as err:
            log.error("Ошибка: ", err)
            log.error("Тип ошибки: ", type(err))
            return err
