from uuid import UUID
from typing import Union, Optional, List

from fastapi import status, HTTPException
from sqlalchemy import update, tuple_, select, exc
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

    async def create(self, user_id: UUID, user_agent: str, refresh_token: str) -> Optional[Entry]:
        """Create Entry"""
        log_message = f'CRUD Create Entry: user_id={user_id}, user_agent={user_agent}, refresh_token={refresh_token}'
        log.debug(log_message)
        new_entry = Entry(
            user_id=user_id,
            user_agent=user_agent,
            refresh_token=refresh_token,
        )
        try:
            self.db_session.add(new_entry)
            await self.db_session.commit()
            return new_entry
        except exc.SQLAlchemyError as err:
            log_message = f'Create entry error: {new_entry.__dict__}'
            log.error(log_message)
            log.error(err)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error creating entry',
            )
        except Exception as err:
            log.error('CRUD Entry Create Unknown Error', exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error creating entry',
            )

    async def delete(self, id: Union[str, UUID]) -> Optional[UUID]:
        """Delete Entry"""
        log_message = f'CRUD Delete Entry: id={id}'
        log.debug(log_message)
        try:
            query = update(Entry). \
                where(Entry.uuid == id). \
                values(is_active=False).returning(Entry.uuid)
            res = await self.db_session.execute(query)
            await self.db_session.commit()
            deleted_entry_id_row = res.fetchone()
            if deleted_entry_id_row is not None:
                return deleted_entry_id_row[0]
        except exc.SQLAlchemyError as err:
            log_message = f'Delete entry error: entry uuid = {id}'
            log.error(log_message)
            log.error(err)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error deleting entry',
            )
        except Exception as err:
            log.error('CRUD Entry Delete Unknown Error', exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error deleting entry',
            )

    async def get(self, id: UUID) -> Optional[Entry]:
        """Get Entry"""
        log_message = f'CRUD Get Entry: id={id}'
        log.debug(log_message)
        try:
            query = select(Entry).where(Entry.uuid == id)
            res = await self.db_session.execute(query)
            entry_row = res.fetchone()
            if entry_row is not None:
                return entry_row[0]
        except exc.SQLAlchemyError as err:
            log_message = f'Get query error: entry uuid = {id}'
            log.error(log_message)
            log.error(err)
        except Exception as err:
            log.error('CRUD Entry Get Unknown Error', exc_info=True)

    async def update(self, id: UUID, **kwargs) -> Optional[UUID]:
        """Update Entry"""
        log_message = f'CRUD Update Entry: id={id}'
        log.debug(log_message)
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
        except exc.SQLAlchemyError as err:
            log_message = f'Update entry error: entry uuid = {id}'
            log.error(log_message)
            log.error(err)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error updating entry',
            )
        except Exception as err:
            log.error('CRUD Entry Update Unknown Error', exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error updating entry',
            )

    async def get_by_user_id(self,
                             user_id: UUID,
                             unique: bool = False,
                             only_active: bool = False,
                             page_size: int = None,
                             page_number: int = None,
                             ) -> Optional[List[Entry]]:
        """Get Entry User by id"""
        log_message = f'CRUD Get Entry User by id: user_id={user_id}, unique={unique}, only_active={only_active}'
        log.debug(log_message)
        try:
            query = select(Entry).where(Entry.user_id == user_id)
            if only_active:
                query = query.where(Entry.is_active == True)
            if unique:
                query = query.distinct(tuple_(Entry.user_agent, Entry.is_active))
            if page_size:
                query = query.limit(page_size)
            if page_number:
                query = query.offset(page_number * page_size - page_size)
            res = await self.db_session.execute(query)
            entries = res.scalars().fetchall()
            return entries
        except exc.SQLAlchemyError as err:
            log_message = f'Get entry by user uuid error: user uuid = {user_id}'
            log.error(log_message)
            log.error(err)

        except Exception as err:
            log.error('CRUD Entry Get by user_id query Unknown Error', exc_info=True)

    async def get_by_user_agent(self,
                                user_agent: str,
                                only_active: bool = False) -> Optional[Union[Entry, None, Exception]]:
        """Get Entry by User_agent"""
        log_message = f'CRUD Get Entry by User_agent: user_agent={user_agent}, only_active={only_active}'
        log.debug(log_message)
        try:
            query = select(Entry).where(Entry.user_agent == user_agent)
            if only_active:
                query = query.where(Entry.is_active == True)
            res = await self.db_session.execute(query)
            entry_row = res.fetchone()
            if entry_row is not None:
                return entry_row[0]
        except exc.SQLAlchemyError as err:
            log_message = f'Get entry by user agent error: user agent = {user_agent}'
            log.error(log_message)
            log.error(err)
        except Exception as err:
            log.error('CRUD Entry Get by user_agent Unknown Error', exc_info=True)
