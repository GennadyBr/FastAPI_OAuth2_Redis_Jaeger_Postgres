from uuid import UUID

from pydantic import BaseModel, EmailStr, SecretStr


class UserCreate(BaseModel):
    name: str
    surname: str
    login: str
    email: EmailStr
    password: SecretStr


class User(BaseModel):
    uuid: UUID
    name: str
    surname: str
    login: str
    email: EmailStr
    password: SecretStr


class ChangeUserData(BaseModel):
    login: str = None
    name: str = None
    surname: str = None
    email: EmailStr = None


class ChangeUserPwd(BaseModel):
    old_password: SecretStr
    new_password: SecretStr
