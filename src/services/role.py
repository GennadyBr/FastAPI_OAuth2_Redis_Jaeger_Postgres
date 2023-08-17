import uuid
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import List, Optional

from fastapi import status, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from crud.role import RoleDAL
from crud.user_role import UserRoleDAL
from crud.user import UserDAL
from db.session import get_db
from models.role import RoleResponse


class RoleServiceBase(ABC):

    @abstractmethod
    async def create_role(self, role_name: str) -> Optional[RoleResponse]:
        """Create new role in db"""

    @abstractmethod
    async def read_role(self, role_id: uuid.UUID) -> Optional[RoleResponse]:
        """Read role from db"""

    async def read_roles(self) -> Optional[List[RoleResponse]]:
        """Read all roles from db"""

    @abstractmethod
    async def update_role(self, role_id: uuid.UUID, new_name: str) -> bool:
        """Update role in db"""

    @abstractmethod
    async def delete_role(self, role_id: uuid.UUID) -> bool:
        """Delete role from db"""

    @abstractmethod
    async def get_user_access_area(self, user_id: uuid.UUID) -> RoleResponse:
        """Get access area for user by its id"""

    @abstractmethod
    async def set_role_to_user(self, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
        """Set a new or additional role to user"""

    @abstractmethod
    async def remove_role_from_user(self, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
        """Remove role from users roles"""


class RoleService(RoleServiceBase):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_role(self, role_name: str) -> Optional[RoleResponse]:
        async with self.db as session:
            async with session.begin():
                role_dal = RoleDAL(session)
                role_exists = await role_dal.get_by_name(role_name)
                if role_exists:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail='Role already exist',
                    )
                try:
                    role = await role_dal.create(name=role_name)
                    return RoleResponse(uuid=role.uuid, name=role.name)
                except Exception:
                    return

    async def read_role(self, role_id: uuid.UUID) -> Optional[RoleResponse]:
        async with self.db as session:
            async with session.begin():
                role_dal = RoleDAL(session)
                role_exists = await role_dal.get(role_id)
                if not role_exists:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail='Role does not exist',
                    )
                try:
                    role = await role_dal.get(id=role_id)
                    return RoleResponse(uuid=role.uuid, name=role.name)
                except Exception:
                    return

    async def read_roles(self) -> Optional[List[RoleResponse]]:
        async with self.db as session:
            async with session.begin():
                role_dal = RoleDAL(session)
                try:
                    roles = await role_dal.get_all()
                    return [RoleResponse(uuid=role.uuid, name=role.name) for role in roles]
                except Exception:
                    return

    async def update_role(self, role_id: uuid.UUID, name: str) -> Optional[RoleResponse]:
        async with self.db as session:
            async with session.begin():
                role_dal = RoleDAL(session)
                role_exists = await role_dal.get(role_id)
                if not role_exists:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail='Role does not exist',
                    )
                try:
                    updated_role_id = await role_dal.update(id=role_id, name=name)
                except Exception:
                    return

        updated_role = await self.read_role(updated_role_id)
        return updated_role

    async def delete_role(self, role_id: uuid.UUID) -> bool:
        async with self.db as session:
            async with session.begin():
                role_dal = RoleDAL(session)
                role_exists = await role_dal.get(role_id)
                if not role_exists:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail='Role does not exist',
                    )
                try:
                    deleted_role_id = await role_dal.delete(uuid=role_id)
                    return bool(deleted_role_id)
                except Exception:
                    return

    async def get_user_access_area(self, user_id: uuid.UUID) -> List[RoleResponse]:
        async with self.db as session:
            async with session.begin():
                role_dal = RoleDAL(session)
                user_dal = UserDAL(session)
                user_exists = await user_dal.get(user_id)
                if not user_exists:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail='User does not exist',
                    )
                try:
                    user_roles = await role_dal.get_by_user_id(user_id)
                    return [RoleResponse(uuid=role.uuid, name=role.name) for role in user_roles]
                except Exception:
                    return

    async def set_role_to_user(self, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
        async with self.db as session:
            async with session.begin():
                user_role_dal = UserRoleDAL(session)
                role_dal = RoleDAL(session)
                user_dal = UserDAL(session)

                user_exists = await user_dal.get(user_id)
                if not user_exists:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail='User does not exist',
                    )

                role_exists = await role_dal.get(role_id)
                if not role_exists:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail='Role does not exist',
                    )

                try:
                    new_user_role = await user_role_dal.create(user_id, role_id)
                    return bool(new_user_role)
                except Exception:
                    return

    async def remove_role_from_user(self, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
        async with self.db as session:
            async with session.begin():
                role_dal = RoleDAL(session)
                user_dal = UserDAL(session)

                user_exists = await user_dal.get(user_id)
                if not user_exists:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail='User does not exist',
                    )

                role_exists = await role_dal.get(role_id)
                if not role_exists:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail='Role does not exist',
                    )

                try:
                    await role_dal.delete_by_user_id_and_role_id(user_id, role_id)
                    return True
                except Exception:
                    return


@lru_cache()
def get_role_service(db: AsyncSession = Depends(get_db)) -> RoleService:
    return RoleService(db=db)
