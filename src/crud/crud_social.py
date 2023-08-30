from uuid import UUID
from typing import Union, Optional, List

from fastapi import status, HTTPException
from sqlalchemy import update, select, exc
from sqlalchemy.ext.asyncio import AsyncSession

import logging.config
from core.logger import LOGGING

logging.config.dictConfig(LOGGING)
log = logging.getLogger(__name__)

from db.models import UserSocial
from crud.base_classes import CrudBase


class UserSocialDAL(CrudBase):
    """Data Access Layer for operation CRUD"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, user_id: UUID, sub_id, provider: str) -> Optional[UserSocial]:
        """Create User_socials"""
        log_message = f'CRUD Create user social: user_id={user_id}, sub_id={sub_id}, provider={provider}'
        log.debug(log_message)
        new_user_social = UserSocial(
            user_id=user_id,
            sub_id=str(sub_id),
            provider=provider,
        )
        try:
            self.db_session.add(new_user_social)
            await self.db_session.commit()
            return new_user_social
        except exc.SQLAlchemyError as err:
            log_message = f'Create user social error: {new_user_social.__dict__}'
            log.error(log_message)
            log.error(err)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error creating user social',
            )
        except Exception:
            log.error('CRUD user social Create Unknown Error', exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error creating user social',
            )

    async def delete(self, id: Union[str, UUID]) -> Optional[UUID]:
        """Delete User_socials"""
        log_message = f'CRUD Delete User_socials: id={id}'
        log.debug(log_message)
        try:
            query = update(UserSocial). \
                where(UserSocial.uuid == id). \
                returning(UserSocial.uuid)
            res = await self.db_session.execute(query)
            await self.db_session.commit()
            deleted_user_social_id_row = res.fetchone()
            if deleted_user_social_id_row is not None:
                return deleted_user_social_id_row[0]
        except exc.SQLAlchemyError as err:
            log_message = f'Delete enuser socialtry error: user social uuid = {id}'
            log.error(log_message)
            log.error(err)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error deleting user social',
            )
        except Exception:
            log.error('CRUD user social Delete Unknown Error', exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error deleting user social',
            )

    async def get(self, id: UUID) -> Optional[UserSocial]:
        """Get User_socials"""
        log_message = f'CRUD Get User_socials: id={id}'
        log.debug(log_message)
        try:
            query = select(UserSocial).where(UserSocial.uuid == id)
            res = await self.db_session.execute(query)
            user_social_row = res.fetchone()
            if user_social_row is not None:
                return user_social_row[0]
        except exc.SQLAlchemyError as err:
            log_message = f'Get query error: user social uuid = {id}'
            log.error(log_message)
            log.error(err)
        except Exception:
            log.error('CRUD user social Get Unknown Error', exc_info=True)

    async def update(self, id: UUID, **kwargs) -> Optional[UUID]:
        """Update User_socials"""
        log_message = f'CRUD Update User_socials: id={id}'
        log.debug(log_message)
        try:
            query = update(UserSocial). \
                where(UserSocial.uuid == id). \
                values(kwargs). \
                returning(UserSocial.uuid)
            res = await self.db_session.execute(query)
            await self.db_session.commit()
            update_user_social_id_row = res.fetchone()
            if update_user_social_id_row is not None:
                return update_user_social_id_row[0]
        except exc.SQLAlchemyError as err:
            log_message = f'Update user social error: user social uuid = {id}'
            log.error(log_message)
            log.error(err)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error updating user social',
            )
        except Exception:
            log.error('CRUD Entry Update Unknown Error', exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error updating user social',
            )

    async def get_by_user_id(self,
                             user_id: UUID,
                             ) -> Optional[List[UserSocial]]:
        """Get User_socials by id"""
        log_message = f'CRUD Get User_socials User by id: user_id={user_id}'
        log.debug(log_message)
        try:
            query = select(UserSocial).where(UserSocial.user_id == user_id)
            res = await self.db_session.execute(query)
            user_socials = res.scalars().fetchall()
            return user_socials
        except exc.SQLAlchemyError as err:
            log_message = f'Get user social by user uuid error: user uuid = {user_id}'
            log.error(log_message)
            log.error(err)

        except Exception:
            log.error('CRUD user social Get by user_id query Unknown Error', exc_info=True)
