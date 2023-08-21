from uuid import UUID
from typing import Union

from fastapi import status, HTTPException
from sqlalchemy import update, and_, select, exc
from sqlalchemy.ext.asyncio import AsyncSession

import logging.config
from core.logger import LOGGING

logging.config.dictConfig(LOGGING)
log = logging.getLogger(__name__)

from db.models import User
from crud.base_classes import CrudBase


###########################################################
# BLOCK FOR INTERACTION WITH DATABASE IN BUSINESS CONTEXT #
###########################################################

class UserDAL(CrudBase):
    """Data Access Layer for operation user CRUD"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(
            self, name: str, surname: str, login: str, email: str, password: str) -> Union[User, Exception]:
        """Create User"""
        log_message = f'CRUD Create User: name={name}, surname={surname}, login={login}, email={email}, password={password}'
        log.debug(log_message)
        try:
            """Create User"""
            new_user = User(
                name=name,
                surname=surname,
                login=login,
                email=email,
                password=password
            )
            self.db_session.add(new_user)
            await self.db_session.commit()
            return new_user
        except exc.SQLAlchemyError as err:
            log_message = f'Create user error: {new_user.__dict__}'
            log.error(log_message)
            log.error(err)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='CRUD User Create query SQLAlchemyError',
            )
        except Exception as err:
            log.error('CRUD User Create Unknown Error', exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='CRUD User Create Unknown Error',
            )

    async def delete(self, id: Union[str, UUID]) -> Union[UUID, None, Exception]:
        """Delete User"""
        log_message = f'CRUD Delete User: id={id}'
        log.debug(log_message)
        try:
            query = update(User). \
                where(and_(User.uuid == id, User.is_active == True)). \
                values(is_active=False).returning(User.uuid)
            res = await self.db_session.execute(query)
            await self.db_session.commit()
            deleted_user_id_row = res.fetchone()
            if deleted_user_id_row is not None:
                return deleted_user_id_row[0]
        except exc.SQLAlchemyError as err:
            log_message = f'Delete user error: uuid = {id}'
            log.error(log_message)
            log.error(err)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='CRUD User Delete query SQLAlchemyError',
            )
        except Exception as err:
            log.error('CRUD User Delete Unknown Error', exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='CRUD User Delete Unknown Error',
            )

    async def get(self, id: UUID) -> Union[User, None, Exception]:
        """Get User"""
        log_message = f'CRUD Get User: id={id}'
        log.debug(log_message)
        try:
            query = select(User).where(User.uuid == id)
            res = await self.db_session.execute(query)
            user_row = res.fetchone()
            if user_row is not None:
                return user_row[0]
        except exc.SQLAlchemyError as err:
            log_message = f'Get user error: uuid = {id}'
            log.error(log_message)
            log.error(err)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='CRUD User Get query SQLAlchemyError',
            )
        except Exception as err:
            log.error('CRUD User Get Unknown Error', exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='CRUD User Get Unknown Error',
            )

    async def update(self, id: UUID, **kwargs) -> Union[UUID, None, Exception]:
        """Update User"""
        log_message = f'CRUD Update User: id={id}, {kwargs}'
        log.debug(log_message)
        try:
            query = update(User). \
                where(User.uuid == id). \
                values(kwargs). \
                returning(User.uuid)
            res = await self.db_session.execute(query)
            await self.db_session.commit()
            update_user_id_row = res.fetchone()
            if update_user_id_row is not None:
                return update_user_id_row[0]
        except exc.SQLAlchemyError as err:
            log_message = f'Update user error: uuid = {id}'
            log.error(log_message)
            log.error(err)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='CRUD User Update query SQLAlchemyError',
            )
        except Exception as err:
            log.error('CRUD User Update Unknown Error', exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='CRUD User Update Unknown Error',
            )

    async def get_by_email(self, email: str) -> Union[User, None, Exception]:
        """Get User by Email"""
        log_message = f'CRUD Get User by Email: email={email}'
        log.debug(log_message)
        try:
            query = select(User).where(User.email == email)
            res = await self.db_session.execute(query)
            user_row = res.fetchone()
            if user_row is not None:
                return user_row[0]
        except exc.SQLAlchemyError as err:
            log_message = f'Get user by email error: email = {email}'
            log.error(log_message)
            log.error(err)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='CRUD User Get by email query SQLAlchemyError',
            )
        except Exception as err:
            log.error('CRUD User Get by email Unknown Error', exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='CRUD User Get by email Unknown Error',
            )

    async def get_by_login(self, login: str) -> Union[User, None, Exception]:
        """Get User by Login"""
        log_message = f'CRUD Get User by Login: login={login}'
        log.debug(log_message)
        try:
            query = select(User).where(User.login == login)
            res = await self.db_session.execute(query)
            user_row = res.fetchone()
            if user_row is not None:
                return user_row[0]
        except exc.SQLAlchemyError as err:
            log_message = f'Get user by login error: login = {login}'
            log.error(log_message)
            log.error(err)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='CRUD User Get by login query SQLAlchemyError',
            )
        except Exception as err:
            log.error('CRUD User Get by login Unknown Error', exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='CRUD User Get by login Unknown Error',
            )
