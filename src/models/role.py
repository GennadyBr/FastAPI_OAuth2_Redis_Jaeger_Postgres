import uuid

from fastapi import HTTPException
from pydantic import BaseModel, validator

from models.base import TunedModel


class ShowRole(TunedModel):
    """это класс ответа для пользователя, поэтому JSON TunedModel"""
    id: uuid.UUID  # в алхимии другой UUID из алхимии
    name: str


class ShowUserRole(TunedModel):
    """это класс ответа для пользователя, поэтому JSON TunedModel"""
    id: uuid.UUID
    user_id: uuid.UUID
    role_id: uuid.UUID


class RoleCreate(BaseModel):
    """это класс обработки входящего запроса поэтому не надо JSON TunedModel"""
    name: str

    @validator("name")
    def validate_name(cls, value):
        if not value.isalpha():
            raise HTTPException(
                status_code=422, detail="Name should contains only letters"
            )
        return value
