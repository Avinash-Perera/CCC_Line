from fastapi import Depends
from bin.services.db_services.role_service import RoleService

class RoleController:
    def __init__(self, role_service: RoleService = Depends(RoleService)):
        self.role_service = role_service

    def get_all_roles(self):
        return self.role_service.get_all_roles()

    def get_role_by_name(self, name: str):
        return self.role_service.get_role_by_name(name)

    def get_role_by_id(self, role_id: int):
        return self.role_service.get_role_by_id(role_id)
