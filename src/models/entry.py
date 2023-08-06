import uuid
from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime

from models.base import TunedModel


class ShowEntry(TunedModel):
    """это класс ответа для пользователя, поэтому JSON TunedModel"""
    id: uuid.UUID
    user_id: uuid.UUID
    user_agent: str
    date_time: datetime
    refresh_token: str
    is_active: bool


class EntryCreate(BaseModel):
    """это класс обработки входящего запроса поэтому не надо JSON TunedModel"""
    # id: uuid.UUID
    user_id: uuid.UUID
    user_agent: str
    # date_time: datetime
    refresh_token: str
    # is_active: bool
