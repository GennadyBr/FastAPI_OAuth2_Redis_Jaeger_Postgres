import uuid
from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from models.role import RoleResponse
from services.role import RoleService, get_role_service

router = APIRouter()


@router.post(
    '',
    response_model=RoleResponse,
    response_model_include={"id", "name"},
    summary="Post request for new role creation",
    description="Creates a new role and returns a new role object",
    response_description="Uuid, name of the role"
)
async def create_new_role(role_name: str, role_service: RoleService = Depends(get_role_service)):
    new_role = await role_service.create_role(role_name)
    if not new_role:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Role is not created')
    # new_role = RoleResponse(**new_role)
    return new_role


@router.put(
    '',
    response_model=RoleResponse,
    response_model_include={"id", "name"},
    summary="Put request for updating existed role",
    description="Updates an existed role and returns a new role object",
    response_description="Uuid, name of the role"
)
async def update_existed_role(role_id: uuid.UUID,
                              new_role_name: str,
                              role_service: RoleService = Depends(get_role_service)):
    new_role = await role_service.update_role(role_id, new_role_name)
    if not new_role:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Role is not updated')
    # new_role = RoleResponse(**new_role)
    return new_role


@router.get(
    '',
    response_model=RoleResponse,
    response_model_include={"id", "name"},
    summary="Get request for existed role",
    description="Gets an existed role and returns a new role object",
    response_description="Uuid, name of the role"
)
async def get_existed_role(role_id: uuid.UUID,
                           role_service: RoleService = Depends(get_role_service)):
    new_role = await role_service.read_role(role_id)
    if not new_role:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Role is not found')
    # new_role = RoleResponse(**new_role)
    return new_role


@router.delete(
    '',
    response_model=bool,
    summary="Delete request for existed role",
    description="Deletes an existed role and returns a bool object",
    response_description="True or False"
)
async def delete_existed_role(role_id: uuid.UUID,
                              role_service: RoleService = Depends(get_role_service)):
    result = await role_service.delete_role(role_id)
    if not result:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Role is not found for deleting')
    # new_role = RoleResponse(**new_role)
    return bool(result)


@router.get(
    '',
    response_model=List[RoleResponse],
    response_model_include={"id", "name"},
    summary="Get user's roles",
    description="Gets a list of user's roles ",
    response_description="Uuid, name of the role"
)
async def get_user_role(user_id: uuid.UUID,
                        role_service: RoleService = Depends(get_role_service)):
    roles = await role_service.get_user_access_area(user_id)
    if not roles:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Roles are not found')
    # new_role = RoleResponse(**new_role)
    return roles


@router.post(
    '',
    # response_model=UserRolesResponse,
    response_model_include={"id", "username", "roles"},
    summary="Add a new role to user",
    description="Add a new role to user",
    response_description="User object with roles info"
)
async def set_role_to_user(user_id: uuid.UUID, role_id: uuid.UUID,
                           role_service: RoleService = Depends(get_role_service)):
    updated_user = await role_service.set_role_to_user(user_id, role_id)
    if not updated_user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Roles are not found')
    # new_role = RoleResponse(**new_role)
    return updated_user


@router.delete(
    '',
    # response_model=UserRolesResponse,
    response_model_include={"id", "username", "roles"},
    summary="Remove a role from user",
    description="Removes a role from user",
    response_description="User object with roles info"
)
async def remove_role_from_user(user_id: uuid.UUID, role_id: uuid.UUID,
                                role_service: RoleService = Depends(get_role_service)):
    updated_user = await role_service.set_role_to_user(user_id, role_id)
    if not updated_user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Roles are not found')
    # new_role = RoleResponse(**new_role)
    return updated_user
