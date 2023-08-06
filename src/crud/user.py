from sqlalchemy import update, and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID
from typing import Union

from db.models import User
from crud.base_classes import CrudBase

###########################################################
# BLOCK FOR INTERACTION WITH DATABASE IN BUSINESS CONTEXT #
###########################################################

class UserDAL(
    CrudBase):  # User Data Access Layer создание, удаление и все остальные функции взаимодействия с пользователем
    """Data Access Layer for operation user CRUD"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(
            self, name: str, surname: str, login: str, email: str, password: str) -> User:
        """Create User"""
        # сюда позже добавить хеширование паролей
        new_user = User(
            name=name,
            surname=surname,
            login=login,
            email=email,
            password=password
        )
        self.db_session.add(new_user)  # добавление в сессию нового пользователя
        await self.db_session.flush()  # добавление в Постгресс нового пользователя
        # сюда позже можно добавить проверки на существование такого пользователя
        return new_user

    async def delete(self, id: Union[str, UUID]) -> Union[UUID, None]:
        query = update(User). \
            where(and_(User.id == id, User.is_active == True)). \
            values(is_active=False).returning(User.id)
        res = await self.db_session.execute(query)
        deleted_user_id_row = res.fetchone()
        if deleted_user_id_row is not None:
            return deleted_user_id_row[0]

    async def get(self, id: UUID) -> Union[User, None]:
        query = select(User).where(User.id == id)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return user_row[0]

    async def update(self, id: UUID, **kwargs) -> Union[UUID, None]:
        query = update(User). \
            where(and_(User.id == id, User.is_active == True)). \
            values(kwargs). \
            returning(User.id)
        res = await self.db_session.execute(query)
        update_user_id_row = res.fetchone()
        if update_user_id_row is not None:
            return update_user_id_row[0]
