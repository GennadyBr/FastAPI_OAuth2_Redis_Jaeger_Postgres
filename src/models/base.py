import uuid
from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, validator, constr
from typing import Optional
from pydantic.types import constr


class TunedModel(BaseModel):  # наследуется от BaseModel pydentic
    class Config:
        """tells pydentic to conver even non dict obj to json"""
        # это класс для создания настроек которые будут общими во всех моделях
        orm_mode = True  # это будет переводить все подряд в JSON


class DeleteResponse(BaseModel):
    deleted_id: uuid.UUID


class UpdateResponse(BaseModel):
    updated_id: uuid.UUID


class UpdateRequest(BaseModel):
    name: Optional[constr(min_length=1)]
    surname: Optional[constr(min_length=1)]
    login: Optional[str]
    email: Optional[EmailStr]
    is_active: Optional[bool]
    password: Optional[str]
    user_id: Optional[uuid.UUID]
    user_agent: Optional[str]
    refresh_token: Optional[str]


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
