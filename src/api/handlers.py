from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Union

from models.pydentic import UserCreate, ShowUser, RoleCreate, ShowRole, DeleteUserResponse
from services.dals import UserDAL, RoleDAL # Data Access Layer создание, удаление и все остальные функции взаимодействия с пользователем

from db.session import get_db

user_router = APIRouter()  # инициализируем роутер для "/user"
role_router = APIRouter()  # инициализируем роутер для "/role"

########
# USER #
########
async def _create_new_user(body: UserCreate, db) -> ShowUser:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user = await user_dal.create(  # создаем юзера в алхимии и получаем его обратно с id и is_active
                name=body.name,
                surname=body.surname,
                login=body.login,
                email=body.email,
                password=body.password
            )
            return ShowUser(
                uuid=user.uuid,
                name=user.name,
                surname=user.surname,
                login=user.login,
                email=user.email,
                is_active=user.is_active,
                password=user.password,  #
            )

async def _delete_user(user_id, db) -> Union[UUID, None]:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            deleted_user_id = user_dal.delete(user_id=user_id)
            return deleted_user_id


@user_router.post("/", response_model=ShowUser)  # роутер пост запрос доступный через "/" а в mainrouter указано "/user"
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> ShowUser:
    return await _create_new_user(body, db)

@user_router.delete("/", response_model=DeleteUserResponse)
async def delete_user(user_id: UUID, db:AsyncSession=Depends(get_db)) -> DeleteUserResponse:
    delete_user_id = await _delete_user(user_id, db)
    if delete_user_id is None:
        raise HTTPException(status_code=404, detail=f"User with id{user_id} not found")
    return DeleteUserResponse(delete_user_id=delete_user_id)

########
# ROLE #
########
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


