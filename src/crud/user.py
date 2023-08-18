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
            log.error("Create query error", err)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='CRUD User Create query SQLAlchemyError',
            )
        except Exception as err:
            log.error("Unknown error: ", err)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='CRUD User Create Unknown Error',
            )

    async def delete(self, id: Union[str, UUID]) -> Union[UUID, None, Exception]:
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
            log.error("Delete query error", err)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='CRUD User Delete query SQLAlchemyError',
            )
        except Exception as err:
            log.error("Unknown error: ", err)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='CRUD User Delete Unknown Error',
            )

    async def get(self, id: UUID) -> Union[User, None, Exception]:
        try:
            query = select(User).where(User.uuid == id)
            res = await self.db_session.execute(query)
            user_row = res.fetchone()
            if user_row is not None:
                return user_row[0]
        except exc.SQLAlchemyError as err:
            log.error("Get query error", err)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='CRUD User Get query SQLAlchemyError',
            )
        except Exception as err:
            log.error("Unknown error: ", err)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='CRUD User Get Unknown Error',
            )

    async def update(self, id: UUID, **kwargs) -> Union[UUID, None, Exception]:
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
            log.error("Update query error", err)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='CRUD User Update query SQLAlchemyError',
            )
        except Exception as err:
            log.error("Unknown error: ", err)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='CRUD User Update Unknown Error',
            )

    async def get_by_email(self, email: str) -> Union[User, None, Exception]:
        try:
            query = select(User).where(User.email == email)
            res = await self.db_session.execute(query)
            user_row = res.fetchone()
            if user_row is not None:
                return user_row[0]
        except exc.SQLAlchemyError as err:
            log.error("Get by email query error", err)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='CRUD User Get by email query SQLAlchemyError',
            )
        except Exception as err:
            log.error("Unknown error: ", err)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='CRUD User Get by email Unknown Error',
            )

    async def get_by_login(self, login: str) -> Union[User, None, Exception]:
        try:
            query = select(User).where(User.login == login)
            res = await self.db_session.execute(query)
            user_row = res.fetchone()
            if user_row is not None:
                return user_row[0]
        except exc.SQLAlchemyError as err:
            log.error("Get by login query error", err)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='CRUD User Get by login query SQLAlchemyError',
            )
        except Exception as err:
            log.error("Unknown error: ", err)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='CRUD User Get by login Unknown Error',
            )
