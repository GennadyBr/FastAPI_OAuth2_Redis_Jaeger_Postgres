from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from models.pydentic import UserCreate, ShowUser, RoleCreate, ShowRole
from services.dals import UserDAL, RoleDAL # Data Access Layer создание, удаление и все остальные функции взаимодействия с пользователем
from db.session import get_db

user_router = APIRouter()  # инициализируем роутер для "/user"
role_router = APIRouter()  # инициализируем роутер для "/role"


async def _create_new_user(body: UserCreate, db) -> ShowUser:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user = await user_dal.create(  # создаем юзера в алхимии и получаем его обратно с id и is_active
                name=body.name,
                surname=body.surname,
                login=body.login,
                email=body.email,
                hashed_password=body.hashed_password
            )
            return ShowUser(
                uuid=user.uuid,
                name=user.name,
                surname=user.surname,
                login=user.login,
                email=user.email,
                is_active=user.is_active,
                hashed_password=user.hashed_password,  #
            )


@user_router.post("/", response_model=ShowUser)  # роутер пост запрос доступный через "/" а в mainrouter указано "/user"
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> ShowUser:
    return await _create_new_user(body, db)



async def _create_new_role(body: RoleCreate, db) -> ShowRole:
    async with db as session:
        async with session.begin():
            role_dal = RoleDAL(session)
            role = await role_dal.create(  # создаем роль в алхимии и получаем ее обратно
                name=body.name
            )
            return ShowRole(
                uuid=role.uuid,
                name=role.name,
            )


@role_router.post("/", response_model=ShowRole)  # роутер пост запрос доступный через "/" а в mainrouter указано "/role"
async def create_role(body: RoleCreate, db: AsyncSession = Depends(get_db)) -> ShowRole:
    return await _create_new_role(body, db)
