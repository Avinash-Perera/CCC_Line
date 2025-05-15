from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session

from bin.db.postgresDB import db_connection
from bin.models.pg_user_model import Role


class RoleService:
    def __init__(self, db: Session = Depends(db_connection)):
        self.db = db

    def get_all_roles(self):
        return self.db.query(Role).all()

    def get_role_by_name(self, name: str):
        role = self.db.query(Role).filter(Role.name == name).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        return role

    def get_role_by_id(self, role_id: int):
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        return role