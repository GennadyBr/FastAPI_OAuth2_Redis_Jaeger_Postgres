from datetime import datetime
import uuid

from pydantic import BaseModel, Field, EmailStr, validator, root_validator, SecretStr


def _only_letters_validator(value: str) -> str:
    if not value.isalpha():
        raise ValueError('name and surname must contains only letters')
    return value


def _pwd_validator(value: str) -> str:
    min_len = 3
    if len(value) < min_len:
        raise ValueError('password must contain at least 3 characters')
    if value.isdigit() or value.isalpha():
        raise ValueError('password must contain letters, numbers and special characters')
    return value


class UserCreateRequest(BaseModel):
    login: str
    name: str
    surname: str
    email: EmailStr
    password: SecretStr

    @validator('name', 'surname')
    def only_letters(cls, value: str) -> str:
        return _only_letters_validator(value)

    @validator('password')
    def pwd_validator(cls, value: SecretStr) -> SecretStr:
        return SecretStr(_pwd_validator(value.get_secret_value()))


class LoginRequest(BaseModel):
    login: str
    password: SecretStr


class ChangeUserPwdRequest(BaseModel):
    old_password: SecretStr
    new_password: SecretStr
    new_password_repeat: SecretStr

    @root_validator
    def password_match(cls, values):
        print(values)
        if values['old_password'] == values['new_password']:
            raise ValueError('The new password must not match the old one')
        if values['new_password'] != values['new_password_repeat']:
            raise ValueError('Passwords do not match')
        _pwd_validator(values['new_password'].get_secret_value())
        return values


class ChangeUserDataRequest(BaseModel):
    login: str = None
    name: str = None
    surname: str = None
    email: EmailStr = None

    @validator('name', 'surname')
    def only_letters(cls, value: str) -> str:
        if value is not None:
            return _only_letters_validator(value)
        return


class UUIDMixIn(BaseModel):
    id: uuid.UUID = Field(..., alias="uuid")

    class Config:
        allow_population_by_field_name = True


class RequestRole(BaseModel):
    name: str = Field()


class RequestNewRoleToUser(BaseModel):
    user_id: uuid.UUID = Field()
    role_id: uuid.UUID = Field()


class UserResponse(BaseModel):
    uuid: uuid.UUID
    name: str
    surname: str
    login: str
    email: EmailStr

    class Config:
        orm_mode = True


class EntryResponse(BaseModel):
    user_agent: str = None
    date_time: datetime
    is_active: bool

    class Config:
        orm_mode = True


class ResponseRole(UUIDMixIn):
    name: str = Field()
