from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from src.modules.auth_service.src.application.ports.roles import IRolRepository
from src.modules.auth_service.src.infrastructure.api.schemas.roles import RolCreate, RolUpdate
from src.modules.auth_service.src.infrastructure.db.models import Rol
from src.shared.exceptions import AlreadyExistsError, NotFoundError, RepositoryError
from datetime import datetime


class RolRepository(IRolRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Rol]:
        try:
            return (
                self.db.query(Rol)
                .filter(Rol.is_active == True)
                .all()
            )
        except SQLAlchemyError as e:
            raise RepositoryError("Error al obtener los roles.") from e

    def get_by_id(self, rol_id: int) -> Optional[Rol]:
        try:
            return (
                self.db.query(Rol)
                .filter(Rol.id_rol == rol_id)
                .first()
            )
        except SQLAlchemyError as e:
            raise RepositoryError("Error al obtener el rol.") from e

    def get_by_nombre(self, nombre: str) -> Optional[Rol]:
        try:
            return (
                self.db.query(Rol)
                .filter(Rol.nombre == nombre)
                .first()
            )
        except SQLAlchemyError as e:
            raise RepositoryError("Error al obtener el rol.") from e

    def create(self, rol_data: RolCreate) -> Rol:
        try:
            db_rol = Rol(
                nombre=rol_data.nombre,
                descripcion=rol_data.descripcion,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            
            self.db.add(db_rol)
            self.db.commit()
            self.db.refresh(db_rol)
            
            return db_rol
        except IntegrityError as e:
            self.db.rollback()
            raise AlreadyExistsError("El rol ya existe.") from e
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError("Error al crear el rol.") from e

    def update(self, rol_id: int, rol_data: RolUpdate) -> Optional[Rol]:
        try:
            db_rol = self.db.query(Rol).filter(Rol.id_rol == rol_id).first()
        except SQLAlchemyError as e:
            raise RepositoryError("Error al actualizar el rol.") from e
        if not db_rol:
            return None

        # Actualizar solo los campos proporcionados
        update_data = rol_data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.now()
        
        for field, value in update_data.items():
            if hasattr(db_rol, field):
                setattr(db_rol, field, value)

        self.db.commit()
        self.db.refresh(db_rol)
        
        return db_rol

    def soft_delete(self, rol_id: int) -> Optional[Rol]:
        from sqlalchemy.sql import func

        try:
            db_rol = self.db.query(Rol).filter(Rol.id_rol == rol_id).first()
        except SQLAlchemyError as e:
            raise RepositoryError("Error al desactivar el rol.") from e
        
        if not db_rol:
            return None

        db_rol.is_active = False
        db_rol.deleted_at = func.now()
        
        try:
            self.db.commit()
            self.db.refresh(db_rol)
            return db_rol
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError("No se pudo eliminar el rol.") from e

    def get_with_permisos(self, rol_id: int) -> Optional[Rol]:
        try:
            return (
                self.db.query(Rol)
                .options(joinedload(Rol.permisos_modulo))
                .filter(Rol.id_rol == rol_id)
                .first()
            )
        except SQLAlchemyError as e:
            raise RepositoryError("Error al obtener el rol con permisos.") from e
