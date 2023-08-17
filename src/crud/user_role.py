from sqlalchemy import update, select, exc
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID
from typing import List, Union

import logging.config
from core.logger import LOGGING

logging.config.dictConfig(LOGGING)
log = logging.getLogger(__name__)

from db.models import UserRole
from crud.base_classes import CrudBase


###########################################################
# BLOCK FOR INTERACTION WITH DATABASE IN BUSINESS CONTEXT #
###########################################################

class UserRoleDAL(CrudBase):
    """Data Access Layer for operation user_role CRUD"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(
            self, user_id: UUID, role_id: UUID) -> Union[UserRole, Exception]:
        """Create UserRole"""
        log_message = f"CRUD Create UserRole: user_id={user_id}, role_id={role_id}"
        log.info(log_message)
        try:
            new_user_role = UserRole(
                user_id=user_id,
                role_id=role_id
            )
            self.db_session.add(new_user_role)
            await self.db_session.commit()
            # сюда позже можно добавить проверки на существование такого пользователя
            return new_user_role
        except exc.SQLAlchemyError as err:
            log.error("Insert query error", err)
            return err
        except Exception as err:
            log.error("Unknown error: ", err)
            return err

    # удаление записи по uuid
    async def delete(self, uuid: Union[str, UUID]) -> Union[UUID, None, Exception]:
        """Delete UserRole by id"""
        log_message = f"CRUD Delete UserRole by id: uuid={uuid}"
        log.info(log_message)
        try:
            user_role = await self.db_session.get(UserRole, uuid)
            await self.db_session.delete(user_role)
            await self.db_session.commit()
            return user_role.uuid
        except exc.SQLAlchemyError as err:
            log.error("Insert query error", err)
            return err
        except Exception as err:
            log.error("Unknown error: ", err)
            return err

    # удаление записи по user_id предполагается что эта функция будет вызываться в цикле перебора по user_id
    async def delete_by_user_id(self, user_id: Union[str, UUID]) -> Union[UUID, None, Exception]:
        """Delete UserRole by user_id"""
        log_message = f"CRUD Delete UserRole by user_id: user_id={user_id}"
        log.info(log_message)
        try:
            user_role = await self.db_session.get(UserRole, user_id)
            await self.db_session.delete(user_role)
            await self.db_session.commit()
            return user_role.uuid
        except exc.SQLAlchemyError as err:
            log.error("Insert query error", err)
            return err
        except Exception as err:
            log.error("Unknown error: ", err)
            return err

    # удаление записи по role_id предполагается что эта функция будет вызываться в цикле перебора по role_id
    async def delete_by_role_id(self, role_id: Union[str, UUID]) -> Union[UUID, None, Exception]:
        """Delete UserRole by role_id"""
        log_message = f"CRUD Delete UserRole by role_id: role_id={role_id}"
        log.info(log_message)
        try:
            user_role = await self.db_session.get(UserRole, role_id)
            await self.db_session.delete(user_role)
            await self.db_session.commit()
            return user_role.uuid
        except exc.SQLAlchemyError as err:
            log.error("Insert query error", err)
            return err
        except Exception as err:
            log.error("Unknown error: ", err)
            return err

    async def get(self, uuid: UUID) -> Union[UserRole, None, Exception]:
        """Get UserRole by id"""
        log_message = f"CRUD Get UserRole by id: uuid={uuid}"
        log.info(log_message)
        try:
            query = select(UserRole).where(UserRole.uuid == uuid)
            res = await self.db_session.execute(query)
            user_role_row = res.fetchone()
            if user_role_row is not None:
                return user_role_row[0]
        except exc.SQLAlchemyError as err:
            log.error("Insert query error", err)
            return err
        except Exception as err:
            log.error("Unknown error: ", err)
            return err

    async def get_by_user_id(self, user_id: UUID) -> Union[List[UserRole], None, Exception]:
        """Get UserRole by user_id"""
        log_message = f"CRUD Get UserRole by user_id: user_id={user_id}"
        log.info(log_message)
        try:
            query = select(UserRole).where(UserRole.user_id == user_id)
            res = await self.db_session.execute(query)
            user_role_rows = res.fetchall()
            if user_role_rows is not None:
                return [row[0] for row in user_role_rows]
        except exc.SQLAlchemyError as err:
            log.error("Insert query error", err)
            return err
        except Exception as err:
            log.error("Unknown error: ", err)
            return err

    async def get_by_role_id(self, role_id: UUID) -> Union[List[UserRole], None, Exception]:
        """Get UserRole by role_id"""
        log_message = f"CRUD Get UserRole by role_id: role_id={role_id}"
        log.info(log_message)
        try:
            query = select(UserRole).where(UserRole.role_id == role_id)
            res = await self.db_session.execute(query)
            user_role_rows = res.fetchall()
            if user_role_rows is not None:
                return [row[0] for row in user_role_rows]
        except exc.SQLAlchemyError as err:
            log.error("Insert query error", err)
            return err
        except Exception as err:
            log.error("Unknown error: ", err)
            return err

    async def update(self, uuid: UUID, **kwargs) -> Union[UUID, None, Exception]:
        """Update UserRole"""
        log_message = f"CRUD Update UserRole: uuid={uuid}, {kwargs}"
        log.info(log_message)
        try:
            query = update(UserRole). \
                where(UserRole.uuid == uuid). \
                values(kwargs). \
                returning(UserRole.uuid)
            res = await self.db_session.execute(query)
            update_user_role_id_row = res.fetchone()
            if update_user_role_id_row is not None:
                return update_user_role_id_row[0]
        except exc.SQLAlchemyError as err:
            log.error("Insert query error", err)
            return err
        except Exception as err:
            log.error("Unknown error: ", err)
            return err
