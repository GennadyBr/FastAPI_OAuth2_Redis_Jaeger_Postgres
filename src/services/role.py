import logging
import uuid
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import List, Optional

from fastapi import status, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import LOGGING
from crud.role import RoleDAL
from crud.user_role import UserRoleDAL
from crud.user import UserDAL
from db.session import get_db
from models.role import RoleResponse

logging.config.dictConfig(LOGGING)
log = logging.getLogger(__name__)


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
        log.info("Init role service")
        self.db = db

    async def create_role(self, role_name: str) -> Optional[RoleResponse]:
        log.info("<<<RoleService.create_role>>>")
        async with self.db as session:
            async with session.begin():
                log.debug("Create new role")
                role_dal = RoleDAL(session)
                role_exists = await role_dal.get_by_name(role_name)
                if role_exists:
                    log.error(f"{status.HTTP_400_BAD_REQUEST}: Role already exists")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail='Role already exist',
                    )
                role = await role_dal.create(name=role_name)
                return RoleResponse(uuid=role.uuid, name=role.name)

    async def read_role(self, role_id: uuid.UUID) -> Optional[RoleResponse]:
        log.info("<<<RoleService.reade_role (by role_id)>>>")
        async with self.db as session:
            async with session.begin():
                log.debug(f"Read role {role_id}")
                role_dal = RoleDAL(session)
                role_exists = await role_dal.get(role_id)
                if not role_exists:
                    log.error(f"{status.HTTP_404_NOT_FOUND}: Role not found {role_id}")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail='Role does not exist',
                    )
                role = await role_dal.get(id=role_id)
                return RoleResponse(uuid=role.uuid, name=role.name)

    async def read_roles(self) -> Optional[List[RoleResponse]]:
        log.info("<<<RoleService.reade_roles>>>")
        async with self.db as session:
            async with session.begin():
                log.debug("Read all roles")
                role_dal = RoleDAL(session)
                roles = await role_dal.get_all()
                return [RoleResponse(uuid=role.uuid, name=role.name) for role in roles]

    async def update_role(self, role_id: uuid.UUID, name: str) -> Optional[RoleResponse]:
        log.info("<<<RoleService.update_role>>>")
        async with self.db as session:
            async with session.begin():
                log.debug(f"Update role: {role_id}; new name: {name}")
                role_dal = RoleDAL(session)
                role_exists = await role_dal.get(role_id)
                if not role_exists:
                    log.error(f"{status.HTTP_404_NOT_FOUND}: Role not found {role_id}")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail='Role does not exist',
                    )
                updated_role_id = await role_dal.update(id=role_id, name=name)

        updated_role = await self.read_role(updated_role_id)
        return updated_role

    async def delete_role(self, role_id: uuid.UUID) -> bool:
        log.info("<<<RoleService.delete_role>>>")
        async with self.db as session:
            async with session.begin():
                role_dal = RoleDAL(session)
                role_exists = await role_dal.get(role_id)
                if not role_exists:
                    log.error(f"{status.HTTP_404_NOT_FOUND}: Role not found {role_id}")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail='Role does not exist',
                    )
                deleted_role_id = await role_dal.delete(uuid=role_id)
                return bool(deleted_role_id)

    async def get_user_access_area(self, user_id: uuid.UUID) -> List[RoleResponse]:
        log.info(f'<<<RoleService.get_user_access_area>>>')
        log_msg = f'{user_id=}'
        log.debug(log_msg)
        async with self.db as session:
            async with session.begin():
                log_msg = f"Get user's access area: {user_id=}"
                log.debug(log_msg)
                role_dal = RoleDAL(session)
                user_dal = UserDAL(session)
                user_exists = await user_dal.get(user_id)
                log_msg = f"{user_id=}, {role_dal=}, {user_dal=}, {user_exists=}"
                log.debug(log_msg)
                if not user_exists:
                    log.error(f"{status.HTTP_404_NOT_FOUND}: User not found {user_id}")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail='User does not exist',
                    )
                user_roles = await role_dal.get_by_user_id(user_id)
                log_msg = f"{user_roles=}"
                log.debug(log_msg)
                return [RoleResponse(uuid=role.uuid, name=role.name) for role in user_roles]

    async def set_role_to_user(self, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
        log.info(f'<<<RoleService.set_role_to_user>>>')
        async with self.db as session:
            async with session.begin():
                log.debug(f"Assign new role to user: user - {user_id}; role_id - {role_id}")
                user_role_dal = UserRoleDAL(session)
                role_dal = RoleDAL(session)
                user_dal = UserDAL(session)

                user_exists = await user_dal.get(user_id)
                if not user_exists:
                    log.error(f"{status.HTTP_404_NOT_FOUND}: User not found {user_id}")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail='User does not exist',
                    )

                role_exists = await role_dal.get(role_id)
                if not role_exists:
                    log.error(f"{status.HTTP_404_NOT_FOUND}: Role not found {role_id}")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail='Role does not exist',
                    )

                new_user_role = await user_role_dal.create(user_id, role_id)
                return bool(new_user_role)

    async def remove_role_from_user(self, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
        log.info(f'<<<RoleService.remove_role_from_user>>>')
        async with self.db as session:
            async with session.begin():
                log.debug(f"Remove role from user: user - {user_id}; role_id - {role_id}")

                role_dal = RoleDAL(session)
                user_dal = UserDAL(session)

                user_exists = await user_dal.get(user_id)
                if not user_exists:
                    log.error(f"{status.HTTP_404_NOT_FOUND}: User not found {user_id}")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail='User does not exist',
                    )

                role_exists = await role_dal.get(role_id)
                if not role_exists:
                    log.error(f"{status.HTTP_404_NOT_FOUND}: Role not found {role_id}")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail='Role does not exist',
                    )

                await role_dal.delete_by_user_id_and_role_id(user_id, role_id)
                return True


@lru_cache()
def get_role_service(db: AsyncSession = Depends(get_db)) -> RoleService:
    log.info(f'<<<Service.role.get_role_service>>>')
    log_msg = f'{db=}, {get_db=}'
    log.debug(log_msg)
    return RoleService(db=db)
