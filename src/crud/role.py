from uuid import UUID
from typing import Union, Optional, List

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
        try:
            new_role = Role(
                name=name,
            )
            self.db_session.add(new_role)  # добавление в сессию новой роли
            await self.db_session.commit()  # добавление в Постгресс новой роли
            return new_role
        except exc.SQLAlchemyError as err:
            log.error("Insert query error", err)
            return err
        except Exception as err:
            log.error("Unknown error: ", err)
            return err

    async def delete(self, uuid: Union[str, UUID]) -> Union[UUID, None, Exception]:
        try:
            role = await self.db_session.get(Role, uuid)
            await self.db_session.delete(role)
            await self.db_session.commit()
            return role.uuid
        except exc.SQLAlchemyError as err:
            log.error("Insert query error", err)
            return err
        except Exception as err:
            log.error("Unknown error: ", err)
            return err

    async def get(self, id: UUID) -> Union[Role, None, Exception]:
        try:
            query = select(Role).where(Role.uuid == id)
            res = await self.db_session.execute(query)
            role_row = res.fetchone()
            if role_row is not None:
                return role_row[0]
        except exc.SQLAlchemyError as err:
            log.error("Insert query error", err)
            return err
        except Exception as err:
            log.error("Unknown error: ", err)
            return err

    async def update(self, id: UUID, **kwargs) -> Union[UUID, None, Exception]:
        try:
            query = update(Role).where(Role.uuid == id).values(kwargs).returning(Role.uuid)
            res = await self.db_session.execute(query)
            update_role_id_row = res.fetchone()
            await self.db_session.commit()
            if update_role_id_row is not None:
                return update_role_id_row[0]
        except exc.SQLAlchemyError as err:
            log.error("Insert query error", err)
            return err
        except Exception as err:
            log.error("Unknown error: ", err)
            return err

    async def get_by_user_id(self, user_id: UUID) -> Optional[Union[List[Role], Exception]]:
        try:
            query = select(Role). \
                join(UserRole, Role.uuid == UserRole.role_id). \
                join(User, UserRole.user_id == User.uuid). \
                where(UserRole.user_id == user_id)
            res = await self.db_session.execute(query)
            role_rows = res.scalars().fetchall()
            return role_rows
        except exc.SQLAlchemyError as err:
            log.error("Insert query error", err)
            return err
        except Exception as err:
            log.error("Unknown error: ", err)
            return err

    async def get_by_name(self, name: str) -> Union[Role, None]:
        try:
            query = select(Role).where(Role.name == name)
            res = await self.db_session.execute(query)
            role_row = res.fetchone()
            if role_row is not None:
                return role_row[0]
        except exc.SQLAlchemyError as err:
            log.error("Insert query error", err)
            return err
        except Exception as err:
            log.error("Unknown error: ", err)
            return err

    async def get_all(self) -> Union[List[Role], None, Exception]:
        try:
            query = select(Role)
            res = await self.db_session.execute(query)
            role_rows = res.fetchall()
            if role_rows:
                return [row[0] for row in role_rows]
        except exc.SQLAlchemyError as err:
            log.error("Insert query error", err)
            return err
        except Exception as err:
            log.error("Unknown error: ", err)
            return err

    async def delete_by_user_id_and_role_id(self,
                                            user_id: UUID,
                                            role_id: UUID) -> Optional[Union[List[Role], Exception]]:
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
            log.error("Insert query error", err)
            return err
        except Exception as err:
            log.error("Unknown error: ", err)
            return err
