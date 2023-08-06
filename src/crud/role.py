from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID
from typing import Union

from db.models import Role
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
        await self.db_session.flush()  # добавление в Постгресс новой роли
        # сюда позже можно добавить проверки на существование такой роли
        return new_role

    async def delete(self, id: Union[str, UUID]) -> Union[UUID, None]:
        role = await self.db_session.get(Role, id)
        await self.db_session.delete(role)
        await self.db_session.commit()
        return role.id

    async def get(self, id: UUID) -> Union[Role, None]:
        query = select(Role).where(Role.id == id)
        res = await self.db_session.execute(query)
        role_row = res.fetchone()
        if role_row is not None:
            return role_row[0]

    async def update(self, id: UUID, **kwargs) -> Union[UUID, None]:
        query = update(Role).where(Role.id == id).values(kwargs).returning(Role.id)
        res = await self.db_session.execute(query)
        update_role_id_row = res.fetchone()
        if update_role_id_row is not None:
            return update_role_id_row[0]
