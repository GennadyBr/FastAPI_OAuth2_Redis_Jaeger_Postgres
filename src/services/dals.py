from sqlalchemy.ext.asyncio import AsyncSession

from db.users import User, Role


###########################################################
# BLOCK FOR INTERACTION WITH DATABASE IN BUSINESS CONTEXT #
###########################################################

class UserDAL:  # User Data Access Layer создание, удаление и все остальные функции взаимодействия с пользователем
    """Data Access Layer for operation user CRUD"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(
            self, name: str, surname: str, login: str, email: str, hashed_password: str) -> User:
        """Create User"""
        # сюда позже добавить хеширование паролей
        new_user = User(
            name=name,
            surname=surname,
            login=login,
            email=email,
            hashed_password=hashed_password
        )
        self.db_session.add(new_user)  # добавление в сессию нового пользователя
        await self.db_session.flush()  # добавление в Постгресс нового пользователя
        # сюда позже можно добавить проверки на существование такого пользователя
        return new_user

    async def read_user():
        pass

    async def update_user():
        pass

    async def del_user():
        pass



class RoleDAL:  # User Data Access Layer создание, удаление и все остальные функции взаимодействия с пользователем
    """Data Access Layer for operation user CRUD"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_role(self, name: str) -> User:
        """Create Role"""
        new_role = Role(
            name=name,
        )
        self.db_session.add(new_role)  # добавление в сессию новой роли
        await self.db_session.flush()  # добавление в Постгресс новой роли
        # сюда позже можно добавить проверки на существование такой роли
        return new_role

    async def read_role():
        pass

    async def update_role():
        pass

    async def del_role():
        pass

