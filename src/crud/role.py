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
        log_message = f'CRUD Create Role: name={name}'
        log.debug(log_message)
        try:
            new_role = Role(
                name=name,
            )
            self.db_session.add(new_role)  # добавление в сессию новой роли
            await self.db_session.commit()  # добавление в Постгресс новой роли
            return new_role
        except exc.SQLAlchemyError as err:
            log_message = f'Create role error: {new_role.__dict__}'
            log.error(log_message)
            log.error(err)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error creating role',
            )
        except Exception as err:
            log.error('CRUD Role Create Unknown Error', exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error creating role',
            )

    async def delete(self, uuid: Union[str, UUID]) -> Union[UUID, None, Exception]:
        """Delete Role"""
        log_message = f'CRUD Delete Role: uuid={uuid}'
        log.debug(log_message)
        try:
            role = await self.db_session.get(Role, uuid)
            await self.db_session.delete(role)
            await self.db_session.commit()
            return role.uuid
        except exc.SQLAlchemyError as err:
            log_message = f'Delete role error: role uuid = {id}'
            log.error(log_message)
            log.error(err)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error deleting role',
            )
        except Exception as err:
            log.error('CRUD Role Delete Unknown Error', exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error deleting role',
            )

    async def get(self, id: UUID) -> Union[Role, None, Exception]:
        """Get Role"""
        log_message = f'CRUD Get Role: id={id}'
        log.debug(log_message)
        try:
            query = select(Role).where(Role.uuid == id)
            res = await self.db_session.execute(query)
            role_row = res.fetchone()
            if role_row is not None:
                return role_row[0]
        except exc.SQLAlchemyError as err:
            log_message = f'Get role error: role uuid = {id}'
            log.error(log_message)
            log.error(err)
        except Exception as err:
            log.error('CRUD Role Get Unknown Error', exc_info=True)

    async def update(self, id: UUID, **kwargs) -> Union[UUID, None, Exception]:
        """Update Role"""
        log_message = f'CRUD Update Role: id={id}'
        log.debug(log_message)
        try:
            query = update(Role).where(Role.uuid == id).values(kwargs).returning(Role.uuid)
            res = await self.db_session.execute(query)
            update_role_id_row = res.fetchone()
            await self.db_session.commit()
            if update_role_id_row is not None:
                return update_role_id_row[0]
        except exc.SQLAlchemyError as err:
            log_message = f'Update role error: role uuid = {id}'
            log.error(log_message)
            log.error(err)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error updating role',
            )
        except Exception as err:
            log.error('CRUD Role Get Unknown Error', exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error updating role',
            )

    async def get_by_user_id(self, user_id: UUID) -> Optional[Union[List[Role], Exception]]:
        """Get Role by User id"""
        log_message = f'CRUD Get Role by User id: user_id={user_id}'
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
            log_message = f'Get role by user id error: user uuid = {user_id}'
            log.error(log_message)
            log.error(err)
        except Exception as err:
            log.error('CRUD Role Get by user_id Unknown Error', exc_info=True)

    async def get_by_name(self, name: str) -> Union[Role, None]:
        """Get Role by Name"""
        log_message = f'CRUD Get Role by Name: name={name}'
        log.debug(log_message)
        try:
            query = select(Role).where(Role.name == name)
            res = await self.db_session.execute(query)
            role_row = res.fetchone()
            if role_row is not None:
                return role_row[0]
        except exc.SQLAlchemyError as err:
            log_message = f'Get role by name error: name = {name}'
            log.error(log_message)
            log.error(err)
        except Exception as err:
            log.error('CRUD Role Get by name Unknown Error', exc_info=True)

    async def get_all(self) -> Union[List[Role], None, Exception]:
        """Get All Roles"""
        log.debug('CRUD Get All Roles')
        try:
            query = select(Role)
            res = await self.db_session.execute(query)
            role_rows = res.fetchall()
            if role_rows:
                return [row[0] for row in role_rows]
        except exc.SQLAlchemyError as err:
            log.error('Get all roles error')
            log.error(err)
        except Exception as err:
            log.error('CRUD Role Get all Unknown Error', exc_info=True)

    async def delete_by_user_id_and_role_id(self,
                                            user_id: UUID,
                                            role_id: UUID) -> Optional[Union[List[Role], Exception]]:
        """Delete Role by User id and Role id"""
        log_message = f'CRUD Delete Role by User id and Role id: user_id={user_id} and role_id={role_id}'
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
            log_message = f'Delete role by user id and role id error: user uuid = {user_id}; role uuid = {role_id}'
            log.error(log_message)
            log.error(err)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error deleting role',
            )
        except Exception as err:
            log.error('CRUD Role Delete by user_id and role_id Unknown Error', exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Error deleting role',
            )
