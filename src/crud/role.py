from uuid import UUID
from typing import Union, Optional, List

from fastapi import status, HTTPException
from sqlalchemy import update, select, exc
from sqlalchemy.ext.asyncio import AsyncSession

import logging.config
from core.logger import LOGGING

logging.config.dictConfig(LOGGING)
log = logging.getLogger(__name__)

from db.models import Role, UserRole, User
from crud.base_classes import CrudBase


###########################################################
# BLOCK FOR INTERACTION WITH DATABASE IN BUSINESS CONTEXT #
###########################################################


class RoleDAL(CrudBase):
    """Data Access Layer for operation role CRUD"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, name: str) -> Union[Role, Exception]:
        """Create Role"""
        log_message = f"CRUD Create Role: name={name}"
        log.debug(log_message)
        try:
            new_role = Role(
                name=name,
            )
            self.db_session.add(new_role)  # добавление в сессию новой роли
            await self.db_session.commit()  # добавление в Постгресс новой роли
            return new_role
        except exc.SQLAlchemyError as err:
            log.error("Create query error", err)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='CRUD Role Create query SQLAlchemyError',
            )
        except Exception as err:
            log.error("CRUD Role Create Unknown Error: ", err)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='CRUD Role Create Unknown Error',
            )

    async def delete(self, uuid: Union[str, UUID]) -> Union[UUID, None, Exception]:
        """Delete Role"""
        log_message = f"CRUD Delete Role: uuid={uuid}"
        log.debug(log_message)
        try:
            role = await self.db_session.get(Role, uuid)
            await self.db_session.delete(role)
            await self.db_session.commit()
            return role.uuid
        except exc.SQLAlchemyError as err:
            log.error("Delete query error", err)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='CRUD Role Delete query SQLAlchemyError',
            )
        except Exception as err:
            log.error("CRUD Role Delete Unknown Error: ", err)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='CRUD Role Delete Unknown Error',
            )

    async def get(self, id: UUID) -> Union[Role, None, Exception]:
        """Get Role"""
        log_message = f"CRUD Get Role: id={id}"
        log.debug(log_message)
        try:
            query = select(Role).where(Role.uuid == id)
            res = await self.db_session.execute(query)
            role_row = res.fetchone()
            if role_row is not None:
                return role_row[0]
        except exc.SQLAlchemyError as err:
            log.error("Get query error", err)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='CRUD Role Get query SQLAlchemyError',
            )
        except Exception as err:
            log.error("CRUD Role Get Unknown Error: ", err)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='CRUD Role Get Unknown Error',
            )

    async def update(self, id: UUID, **kwargs) -> Union[UUID, None, Exception]:
        """Update Role"""
        log_message = f"CRUD Update Role: id={id}"
        log.debug(log_message)
        try:
            query = update(Role).where(Role.uuid == id).values(kwargs).returning(Role.uuid)
            res = await self.db_session.execute(query)
            update_role_id_row = res.fetchone()
            await self.db_session.commit()
            if update_role_id_row is not None:
                return update_role_id_row[0]
        except exc.SQLAlchemyError as err:
            log.error("Update query error", err)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='CRUD Role Update query SQLAlchemyError',
            )
        except Exception as err:
            log.error("CRUD Role Get Unknown Error: ", err)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='CRUD Role Get Unknown Error',
            )

    async def get_by_user_id(self, user_id: UUID) -> Optional[Union[List[Role], Exception]]:
        """Get Role by User id"""
        log_message = f"CRUD Get Role by User id: user_id={user_id}"
        log.debug(log_message)
        try:
            query = select(Role). \
                join(UserRole, Role.uuid == UserRole.role_id). \
                join(User, UserRole.user_id == User.uuid). \
                where(UserRole.user_id == user_id)
            res = await self.db_session.execute(query)
            role_rows = res.scalars().fetchall()
            return role_rows
        except exc.SQLAlchemyError as err:
            log.error("Get by user_id query error", err)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='CRUD Role Get by user_id query SQLAlchemyError',
            )
        except Exception as err:
            log.error("CRUD Role Get by user_id Unknown Error: ", err)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='CRUD Role Get by user_id Unknown Error',
            )

    async def get_by_name(self, name: str) -> Union[Role, None]:
        """Get Role by Name"""
        log_message = f"CRUD Get Role by Name: name={name}"
        log.debug(log_message)
        try:
            query = select(Role).where(Role.name == name)
            res = await self.db_session.execute(query)
            role_row = res.fetchone()
            if role_row is not None:
                return role_row[0]
        except exc.SQLAlchemyError as err:
            log.error("Get by name query error", err)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='CRUD Role Get by name query SQLAlchemyError',
            )
        except Exception as err:
            log.error("CRUD Role Get by name Unknown Error: ", err)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='CRUD Role Get by name Unknown Error',
            )

    async def get_all(self) -> Union[List[Role], None, Exception]:
        """Get All Roles"""
        log_message = f"CRUD Get All Roles"
        log.debug(log_message)
        try:
            query = select(Role)
            res = await self.db_session.execute(query)
            role_rows = res.fetchall()
            if role_rows:
                return [row[0] for row in role_rows]
        except exc.SQLAlchemyError as err:
            log.error("Get all query error", err)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='CRUD Role Get all query SQLAlchemyError',
            )
        except Exception as err:
            log.error("CRUD Role Get all Unknown Error: ", err)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='CRUD Role Get all Unknown Error',
            )

    async def delete_by_user_id_and_role_id(self,
                                            user_id: UUID,
                                            role_id: UUID) -> Optional[Union[List[Role], Exception]]:
        """Delete Role by User id and Role id"""
        log_message = f"CRUD Delete Role by User id and Role id: user_id={user_id} and role_id={role_id}"
        log.debug(log_message)
        try:
            query = select(UserRole). \
                join(Role, Role.uuid == UserRole.role_id). \
                join(User, UserRole.user_id == User.uuid). \
                where(UserRole.user_id == user_id).where(Role.uuid == role_id)
            res = await self.db_session.execute(query)
            role_rows = res.fetchone()
            if role_rows:
                user_role = await self.db_session.get(UserRole, role_rows[0].uuid)
                await self.db_session.delete(user_role)
                await self.db_session.commit()
        except exc.SQLAlchemyError as err:
            log.error("Delete by user_id and role_id query error", err)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='CRUD Role Delete by user_id and role_id query SQLAlchemyError',
            )
        except Exception as err:
            log.error("CRUD Role Delete by user_id and role_id Unknown Error: ", err)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='CRUD Role Delete by user_id and role_id Unknown Error',
            )
