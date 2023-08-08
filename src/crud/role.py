from uuid import UUID
from typing import Union, Optional, List

from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Role, UserRole, User
from crud.base_classes import CrudBase


###########################################################
# BLOCK FOR INTERACTION WITH DATABASE IN BUSINESS CONTEXT #
###########################################################


class RoleDAL(
    CrudBase):  # Role Data Access Layer создание, удаление и все остальные функции взаимодействия с пользователем
    """Data Access Layer for operation role CRUD"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, name: str) -> Role:
        new_role = Role(
            name=name,
        )
        self.db_session.add(new_role)  # добавление в сессию новой роли
        await self.db_session.commit()  # добавление в Постгресс новой роли
        return new_role

    async def delete(self, uuid: Union[str, UUID]) -> Union[UUID, None]:
        role = await self.db_session.get(Role, uuid)
        await self.db_session.delete(role)
        await self.db_session.commit()
        return role.uuid

    async def get(self, id: UUID) -> Union[Role, None]:
        query = select(Role).where(Role.uuid == id)
        res = await self.db_session.execute(query)
        role_row = res.fetchone()
        if role_row is not None:
            return role_row[0]

    async def update(self, id: UUID, **kwargs) -> Union[UUID, None]:
        query = update(Role).where(Role.uuid == id).values(kwargs).returning(Role.uuid)
        res = await self.db_session.execute(query)
        update_role_id_row = res.fetchone()
        await self.db_session.commit()
        if update_role_id_row is not None:
            return update_role_id_row[0]
        
    async def get_by_user_id(self, user_id: UUID) -> Optional[List[Role]]:
        query = select(Role). \
            join(UserRole, Role.uuid == UserRole.role_id). \
            join(User, UserRole.user_id == User.uuid). \
            where(UserRole.user_id == user_id)
        res = await self.db_session.execute(query)
        role_rows = res.scalars().fetchall()
        return role_rows
