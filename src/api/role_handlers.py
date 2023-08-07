from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from typing import Union

from models.role import RoleCreate, ShowRole
from models.base import DeleteResponse, UpdateResponse, UpdateRequest
# Data Access Layer создание, удаление и все остальные функции взаимодействия с пользователем
from crud.role import RoleDAL
from db.session import get_db

role_router = APIRouter()  # инициализируем роутер для "/role"

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


async def _delete_role(uuid, db) -> Union[UUID, str, None]:
    async with db as session:
        async with session.begin():
            role_dal = RoleDAL(session)
            deleted_role_id = await role_dal.delete(uuid=uuid)
            return deleted_role_id


async def _update_role(updated_role_params: dict, uuid: UUID, db) -> Union[UUID, None]:
    async with db as session:
        async with session.begin():
            role_dal = RoleDAL(session)
            updated_role_id = await role_dal.update(
                uuid=uuid,
                **updated_role_params
            )
            return updated_role_id


async def _get_role_by_id(uuid, db) -> Union[ShowRole, None]:
    async with db as session:
        async with session.begin():
            role_dal = RoleDAL(session)
            user = await role_dal.get(
                uuid=uuid,
            )
            if user is not None:
                return ShowRole(
                    uuid=user.uuid,
                    name=user.name,
                )


@role_router.post("/", response_model=ShowRole)  # роутер пост запрос доступный через "/" а в mainrouter указано "/role"
async def create_role(body: RoleCreate, db: AsyncSession = Depends(get_db)) -> ShowRole:
    return await _create_new_role(body, db)


@role_router.delete("/", response_model=DeleteResponse)
async def delete_role(uuid: Union[str, UUID], db: AsyncSession = Depends(get_db)) -> DeleteResponse:
    deleted_id = await _delete_role(uuid, db)
    if deleted_id is None:
        raise HTTPException(status_code=404, detail=f"Role with id('{uuid}') not found")
    return DeleteResponse(deleted_id=deleted_id)


@role_router.get("/", response_model=ShowRole)
async def get_role_by_id(uuid: UUID, db: AsyncSession = Depends(get_db)) -> ShowRole:
    role = await _get_role_by_id(uuid, db)
    if role is None:
        raise HTTPException(status_code=404, detail=f"Role with id('{uuid}') not found.")
    return role


@role_router.patch("/", response_model=UpdateResponse)
async def update_role_by_id(
        uuid: UUID, body: UpdateRequest, db: AsyncSession = Depends(get_db)
) -> UpdateResponse:
    updated_role_params = body.dict(exclude_none=True)
    if updated_role_params == {}:
        raise HTTPException(status_code=422, detail="At least one parameter for role update info should be provided")
    role = await _get_role_by_id(uuid, db)
    if role is None:
        raise HTTPException(status_code=404, detail=f"Role with id('{uuid}') not found.")
    updated_id = await _update_role(updated_role_params=updated_role_params, db=db, uuid=uuid)
    return UpdateResponse(updated_id=updated_id)


