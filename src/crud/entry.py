from sqlalchemy import update, and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from uuid import UUID
from typing import Union

from db.models import Entry
from crud.base_classes import CrudBase


###########################################################
# BLOCK FOR INTERACTION WITH DATABASE IN BUSINESS CONTEXT #
###########################################################

class EntryDAL(
    CrudBase):  # Entry Data Access Layer создание, удаление и все остальные функции взаимодействия с пользователем
    """Data Access Layer for operation CRUD"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, user_id: UUID, user_agent: str, refresh_token: str) -> Entry:
        """Create Entry"""
        new_entry = Entry(
            user_id=user_id,
            user_agent=user_agent,
            refresh_token=refresh_token,
        )
        self.db_session.add(new_entry)  # добавление в сессию нового пользователя
        await self.db_session.flush()  # добавление в Постгресс нового пользователя
        # сюда позже можно добавить проверки на существование такого пользователя
        return new_entry

    async def delete(self, uuid: Union[str, UUID]) -> Union[UUID, None]:
        query = update(Entry). \
            where(and_(Entry.uuid == uuid, Entry.is_active == True)). \
            values(is_active=False).returning(Entry.uuid)
        res = await self.db_session.execute(query)
        deleted_entry_id_row = res.fetchone()
        if deleted_entry_id_row is not None:
            return deleted_entry_id_row[0]

    async def get(self, uuid: UUID) -> Union[Entry, None]:
        query = select(Entry).where(Entry.uuid == uuid)
        res = await self.db_session.execute(query)
        entry_row = res.fetchone()
        if entry_row is not None:
            return entry_row[0]

    async def update(self, uuid: UUID, **kwargs) -> Union[UUID, None]:
        query = update(Entry). \
            where(and_(Entry.uuid == uuid, Entry.is_active == True)). \
            values(kwargs). \
            returning(Entry.uuid)
        res = await self.db_session.execute(query)
        update_entry_id_row = res.fetchone()
        if update_entry_id_row is not None:
            return update_entry_id_row[0]

    async def get_by_user_id(self, user_id: UUID) -> Union[Entry, None]:
        query = select(Entry).where(Entry.user_id == user_id)
        res = await self.db_session.execute(query)
        entry_list = res.fetchall()
        if entry_list is not None:
            return entry_list
