from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from typing import Union

from models.entry import EntryCreate, ShowEntry
from models.base import DeleteResponse, UpdateResponse, UpdateRequest
# Data Access Layer создание, удаление и все остальные функции взаимодействия с пользователем
from crud.entry import EntryDAL

from db.session import get_db

entry_router = APIRouter()  # инициализируем роутер для "/entry"


async def _create_new_entry(body: EntryCreate, db) -> ShowEntry:
    async with db as session:
        async with session.begin():
            entry_dal = EntryDAL(session)
            entry = await entry_dal.create(  # создаем юзера в алхимии и получаем его обратно с id и is_active
                user_id=body.user_id,
                user_agent=body.user_agent,
                refresh_token=body.refresh_token,
            )
            return ShowEntry(
                id=entry.id,
                user_id=entry.user_id,
                user_agent=entry.user_agent,
                date_time=entry.date_time,
                refresh_token=entry.refresh_token,
                is_active=entry.is_active,
            )


async def _delete_entry(id, db) -> Union[UUID, str, None]:
    async with db as session:
        async with session.begin():
            entry_dal = EntryDAL(session)
            deleted_entry_id = await entry_dal.delete(id=id)
            return deleted_entry_id


async def _update_entry(updated_entry_params: dict, id: UUID, db) -> Union[UUID, None]:
    async with db as session:
        async with session.begin():
            entry_dal = EntryDAL(session)
            updated_entry_id = await entry_dal.update(
                id=id,
                **updated_entry_params
            )
            return updated_entry_id


async def _get_entry_by_id(id, db) -> Union[ShowEntry, None]:
    async with db as session:
        async with session.begin():
            entry_dal = EntryDAL(session)
            entry = await entry_dal.get(
                id=id,
            )
            if entry is not None:
                return ShowEntry(
                    id=entry.id,
                    user_id=entry.user_id,
                    user_agent=entry.user_agent,
                    date_time=entry.date_time,
                    refresh_token=entry.refresh_token,
                    is_active=entry.is_active,
                )


@entry_router.post("/", response_model=ShowEntry)  # роутер пост запрос доступный через "/" а в mainrouter указано "/entry"
async def create_entry(body: EntryCreate, db: AsyncSession = Depends(get_db)) -> ShowEntry:
    return await _create_new_entry(body, db)


@entry_router.delete("/", response_model=DeleteResponse)
async def delete_entry(id: Union[str, UUID], db: AsyncSession = Depends(get_db)) -> DeleteResponse:
    deleted_id = await _delete_entry(id, db)
    if deleted_id is None:
        raise HTTPException(status_code=404, detail=f"Entry with id('{id}') not found")
    return DeleteResponse(deleted_id=deleted_id)


@entry_router.get("/", response_model=ShowEntry)
async def get_entry_by_id(id: UUID, db: AsyncSession = Depends(get_db)) -> ShowEntry:
    entry = await _get_entry_by_id(id, db)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"Entry with id('{id}') not found.")
    return entry


@entry_router.patch("/", response_model=UpdateResponse)
async def update_entry_by_id(
        id: UUID, body: UpdateRequest, db: AsyncSession = Depends(get_db)
) -> UpdateResponse:
    updated_entry_params = body.dict(exclude_none=True)
    if updated_entry_params == {}:
        raise HTTPException(status_code=422, detail="At least one parameter for entry update info should be provided")
    entry = await _get_entry_by_id(id, db)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"Entry with id('{id}') not found.")
    updated_id = await _update_entry(updated_entry_params=updated_entry_params, db=db, id=id)
    return UpdateResponse(updated_id=updated_id)
