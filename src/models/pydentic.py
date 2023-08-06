import re
import uuid
from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, validator

##################################
# PYDENTIC BLOCK WITH API MODELS #
##################################

class TunedModel(BaseModel):  # наследуется от BaseModel pydentic
    class Config:
        """tells pydentic to conver even non dict obj to json"""
        # это класс для создания настроек которые будут общими во всех моделях
        orm_mode = True  # это будет переводить все подряд в JSON


class ShowUser(TunedModel):
    """это класс ответа для пользователя, поэтому JSON TunedModel"""
    uuid: uuid.UUID  # в алхимии другой UUID из алхимии
    name: str
    surname: str
    login: str
    email: EmailStr
    is_active: bool
    password: str  #


class ShowRole(TunedModel):
    """это класс ответа для пользователя, поэтому JSON TunedModel"""
    uuid: uuid.UUID  # в алхимии другой UUID из алхимии
    name: str


class ShowEntry(TunedModel):
    """это класс ответа для пользователя, поэтому JSON TunedModel"""
    uuid: uuid.UUID
    user_id: uuid.UUID
    user_agent: str
    date_time: str #потом поставлю datetime
    refresh_token: str
    is_active: bool


class ShowUserRole(TunedModel):
    """это класс ответа для пользователя, поэтому JSON TunedModel"""
    uuid: uuid.UUID
    user_id: uuid.UUID
    role_id: uuid.UUID


class UserCreate(BaseModel):
    """это класс обработки входящего запроса поэтому не надо JSON TunedModel"""
    name: str
    surname: str
    login: str
    email: EmailStr
    password: str

    @validator("name")
    def validate_name(cls, value):
        if not value.isalpha():
            raise HTTPException(
                status_code=422, detail="Name should contains only letters"
            )
        return value

    @validator("surname")
    def validate_surname(cls, value):
        if not value.isalpha():
            raise HTTPException(
                status_code=422, detail="Surname should contains only letters"
            )
        return value


class DeleteUserResponse(BaseModel):
    deleted_user_id: uuid.UUID


class RoleCreate(BaseModel):
    """это класс обработки входящего запроса поэтому не надо JSON TunedModel"""
    name: str