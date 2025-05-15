from fastapi import APIRouter, Depends

from bin.controllers.role_controller import RoleController

role_router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)


@role_router.get("/")
def get_all_roles(
    role_controller: RoleController = Depends(RoleController)
):
    return role_controller.get_all_roles()

@role_router.get("/by-name/{name}")
def get_role_by_name(
    name: str,
    role_controller: RoleController = Depends(RoleController)
):
    return role_controller.get_role_by_name(name)

@role_router.get("/{role_id}")
def get_role_by_id(
    role_id: int,
    role_controller: RoleController = Depends(RoleController)
):
    return role_controller.get_role_by_id(role_id)
