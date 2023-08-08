from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID
from typing import List, Union

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
            self, user_id: UUID, role_id: UUID) -> UserRole:
        """Create UserRole"""
        new_user_role = UserRole(
            user_id=user_id,
            role_id=role_id
        )
        self.db_session.add(new_user_role)
        await self.db_session.commit()
        # сюда позже можно добавить проверки на существование такого пользователя
        return new_user_role

    # удаление записи по uuid
    async def delete(self, uuid: Union[str, UUID]) -> Union[UUID, None]:
        user_role = await self.db_session.get(UserRole, uuid)
        await self.db_session.delete(user_role)
        await self.db_session.commit()
        return user_role.uuid

    # удаление записи по user_id предполагается что эта функция будет вызываться в цикле перебора по user_id
    async def delete_by_user_id(self, user_id: Union[str, UUID]) -> Union[UUID, None]:
        user_role = await self.db_session.get(UserRole, user_id)
        await self.db_session.delete(user_role)
        await self.db_session.commit()
        return user_role.uuid

    # удаление записи по role_id предполагается что эта функция будет вызываться в цикле перебора по role_id
    async def delete_by_role_id(self, role_id: Union[str, UUID]) -> Union[UUID, None]:
        user_role = await self.db_session.get(UserRole, role_id)
        await self.db_session.delete(user_role)
        await self.db_session.commit()
        return user_role.uuid

    async def get(self, uuid: UUID) -> Union[UserRole, None]:
        query = select(UserRole).where(UserRole.uuid == uuid)
        res = await self.db_session.execute(query)
        user_role_row = res.fetchone()
        if user_role_row is not None:
            return user_role_row[0]

    async def get_by_user_id(self, user_id: UUID) -> List[UserRole] | None:
        query = select(UserRole).where(UserRole.user_id == user_id)
        res = await self.db_session.execute(query)
        user_role_rows = res.fetchall()
        if user_role_rows is not None:
            return [row[0] for row in user_role_rows]

    async def get_by_role_id(self, role_id: UUID) -> Union[UserRole, None]:
        # не будет работать в таком виде. Но пока нигде не используется
        query = select(UserRole).where(UserRole.role_id == role_id)
        res = await self.db_session.execute(query)
        user_role_row = res.fetchone()
        if user_role_row is not None:
            return user_role_row[0]

    async def update(self, uuid: UUID, **kwargs) -> Union[UUID, None]:
        query = update(UserRole). \
            where(UserRole.uuid == uuid). \
            values(kwargs). \
            returning(UserRole.uuid)
        res = await self.db_session.execute(query)
        update_user_role_id_row = res.fetchone()
        if update_user_role_id_row is not None:
            return update_user_role_id_row[0]
