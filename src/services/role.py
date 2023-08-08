import uuid
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import List, Optional

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from crud.role import RoleDAL
from crud.user_role import UserRoleDAL
from db.abstract import AbstractCache
from db.redis import get_cache
from db.session import get_db
from models.role import RoleResponse


class RoleCRUD(ABC):
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


class RoleServiceBase(ABC):

    @abstractmethod
    async def get_user_access_area(self, user_id: uuid.UUID) -> RoleResponse:
        """Get access area for user by its id"""

    @abstractmethod
    async def set_role_to_user(self, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
        """Set a new or additional role to user"""

    @abstractmethod
    async def remove_role_from_user(self, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
        """Remove role from users roles"""


class RoleService(RoleCRUD, RoleServiceBase):

    def __init__(self, db: AsyncSession, cache: AbstractCache):
        self.db = db
        self.cache = cache

    async def create_role(self, role_name: str) -> Optional[RoleResponse]:
        async with self.db as session:
            async with session.begin():
                role_dal = RoleDAL(session)
                role = await role_dal.create(name=role_name)
                return RoleResponse(uuid=role.uuid, name=role.name)

    async def read_role(self, role_id: uuid.UUID) -> Optional[RoleResponse]:
        async with self.db as session:
            async with session.begin():
                role_dal = RoleDAL(session)
                role = await role_dal.get(id=role_id)
                return RoleResponse(uuid=role.uuid, name=role.name)

    async def read_roles(self) -> Optional[List[RoleResponse]]:
        async with self.db as session:
            async with session.begin():
                role_dal = RoleDAL(session)
                roles = await role_dal.get_all()
                return [RoleResponse(uuid=role.uuid, name=role.name) for role in roles]

    async def update_role(self, role_id: uuid.UUID, name: str) -> Optional[RoleResponse]:
        async with self.db as session:
            async with session.begin():
                role_dal = RoleDAL(session)
                updated_role_id = await role_dal.update(id=role_id, name=name)

        return await self.read_role(updated_role_id)

    async def delete_role(self, role_id: uuid.UUID) -> bool:
        async with self.db as session:
            async with session.begin():
                role_dal = RoleDAL(session)
                deleted_role_id = await role_dal.delete(uuid=role_id)
                if deleted_role_id:
                    return True
                return False

    async def get_user_access_area(self, user_id: uuid.UUID) -> List[RoleResponse]:
        async with self.db as session:
            async with session.begin():
                role_dal = RoleDAL(session)
                user_roles = await role_dal.get_by_user_id(user_id)
                return [RoleResponse(uuid=role.uuid, name=role.name) for role in user_roles]

    async def set_role_to_user(self, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
        async with self.db as session:
            async with session.begin():
                user_role_dal = UserRoleDAL(session)
                new_user_role = await user_role_dal.create(user_id, role_id)
                if new_user_role:
                    return True
                return False

    async def remove_role_from_user(self, user_id: uuid.UUID, role_id: uuid.UUID):
        async with self.db as session:
            async with session.begin():
                role_dal = RoleDAL(session)
                await role_dal.delete_by_user_id_and_role_id(user_id, role_id)
                res = await role_dal.delete_by_user_id_and_role_id(user_id, role_id)
                if res is None:
                    return True
                return False


@lru_cache()
def get_role_service(db: AsyncSession = Depends(get_db),
                     cache: AbstractCache = Depends(get_cache)) -> RoleService:
    return RoleService(db=db, cache=cache)
