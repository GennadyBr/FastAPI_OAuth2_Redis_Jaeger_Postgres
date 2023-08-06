import uuid
from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, validator

from models.base import TunedModel


##################################
# PYDENTIC BLOCK WITH API MODELS #
##################################


class ShowUser(TunedModel):
    """это класс ответа для пользователя, поэтому JSON TunedModel"""
    id: uuid.UUID  # в алхимии другой UUID из алхимии
    name: str
    surname: str
    login: str
    email: EmailStr
    is_active: bool
    password: str  #


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


