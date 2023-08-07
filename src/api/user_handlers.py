from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from typing import Union

from models.user import UserCreate, ShowUser
from models.base import DeleteResponse, UpdateResponse, UpdateRequest
# Data Access Layer создание, удаление и все остальные функции взаимодействия с пользователем
from crud.user import UserDAL

from db.session import get_db

user_router = APIRouter()  # инициализируем роутер для "/user"


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
                password=user.password,
            )


async def _delete_user(uuid, db) -> Union[UUID, str, None]:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            deleted_user_id = await user_dal.delete(uuid=uuid)
            return deleted_user_id


async def _update_user(updated_user_params: dict, uuid: UUID, db) -> Union[UUID, None]:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            updated_user_id = await user_dal.update(
                uuid=uuid,
                **updated_user_params
            )
            return updated_user_id


async def _get_user_by_id(uuid, db) -> Union[ShowUser, None]:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user = await user_dal.get(
                uuid=uuid,
            )
            if user is not None:
                return ShowUser(
                    uuid=user.uuid,
                    name=user.name,
                    surname=user.surname,
                    login=user.login,
                    email=user.email,
                    is_active=user.is_active,
                    password=user.password,
                )


@user_router.post("/", response_model=ShowUser)  # роутер пост запрос доступный через "/" а в mainrouter указано "/user"
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> ShowUser:
    return await _create_new_user(body, db)


@user_router.delete("/", response_model=DeleteResponse)
async def delete_user(uuid: Union[str, UUID], db: AsyncSession = Depends(get_db)) -> DeleteResponse:
    deleted_id = await _delete_user(uuid, db)
    if deleted_id is None:
        raise HTTPException(status_code=404, detail=f"User with id('{uuid}') not found")
    return DeleteResponse(deleted_id=deleted_id)


@user_router.get("/", response_model=ShowUser)
async def get_user_by_id(uuid: UUID, db: AsyncSession = Depends(get_db)) -> ShowUser:
    user = await _get_user_by_id(uuid, db)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User with id('{uuid}') not found.")
    return user


@user_router.patch("/", response_model=UpdateResponse)
async def update_user_by_id(
        uuid: UUID, body: UpdateRequest, db: AsyncSession = Depends(get_db)
) -> UpdateResponse:
    updated_user_params = body.dict(exclude_none=True)
    if updated_user_params == {}:
        raise HTTPException(status_code=422, detail="At least one parameter for user update info should be provided")
    user = await _get_user_by_id(uuid, db)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User with id('{uuid}') not found.")
    updated_id = await _update_user(updated_user_params=updated_user_params, db=db, uuid=uuid)
    return UpdateResponse(updated_id=updated_id)
