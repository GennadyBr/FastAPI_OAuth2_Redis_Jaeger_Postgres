import uuid
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import List, Optional

from db.abstract import AbstractCache, AbstractDB
from models.role import RoleResponse


class RoleCRUD(ABC):
    @abstractmethod
    async def create_role(self, role_name: str) -> Optional[RoleResponse]:
        """Create new role in db"""

    @abstractmethod
    async def read_role(self, role_id: uuid.UUID) -> Optional[RoleResponse]:
        """Read role from db"""

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
    async def set_role_to_user(self, user_id: uuid.UUID, role_id: uuid.UUID):
        """Set a new or additional role to user"""

    @abstractmethod
    async def remove_role_from_user(self, user_id: uuid.UUID, role_id: uuid.UUID):
        """Remove role from users roles"""


class RoleService(RoleCRUD, RoleServiceBase):

    def __init__(self, db: AbstractDB, cache: AbstractCache):
        self.db = db
        self.cache = cache

    async def create_role(self, role_name: str) -> Optional[RoleResponse]:
        pass

    async def read_role(self, role_id: uuid.UUID) -> Optional[RoleResponse]:
        pass

    async def update_role(self, role_id: uuid.UUID, new_name: str) -> Optional[RoleResponse]:
        pass

    async def delete_role(self, role_id: uuid.UUID) -> bool:
        pass

    async def get_user_access_area(self, user_id: uuid.UUID) -> List[RoleResponse]:
        pass

    async def set_role_to_user(self, user_id: uuid.UUID, role_id: uuid.UUID):
        pass

    async def remove_role_from_user(self, user_id: uuid.UUID, role_id: uuid.UUID):
        pass


@lru_cache()
def get_role_service() -> RoleService:
    return RoleService()
