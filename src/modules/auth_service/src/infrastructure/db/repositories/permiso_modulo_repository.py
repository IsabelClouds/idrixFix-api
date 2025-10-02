from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from src.modules.auth_service.src.application.ports.permisos_modulo import IPermisoModuloRepository
from src.modules.auth_service.src.infrastructure.api.schemas.permisos_modulo import PermisoModuloCreate, PermisoModuloUpdate
from src.modules.auth_service.src.infrastructure.db.models import PermisoModulo
from src.modules.auth_service.src.domain.entities import ModuloEnum
from datetime import datetime
from src.shared.exceptions import AlreadyExistsError, NotFoundError, RepositoryError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


class PermisoModuloRepository(IPermisoModuloRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[PermisoModulo]:
        """Obtiene todos los permisos de módulo activos"""
        try:
            return (
                self.db.query(PermisoModulo)
                .options(joinedload(PermisoModulo.rol))
                .filter(PermisoModulo.is_active == True)
                .all()
            )
        except SQLAlchemyError as e:
            raise RepositoryError("Error al obtener los permisos de módulo.") from e

    def get_by_id(self, permiso_id: int) -> Optional[PermisoModulo]:
        """Obtiene un permiso por ID"""
        try:
            return (
                self.db.query(PermisoModulo)
                .options(joinedload(PermisoModulo.rol))
                .filter(PermisoModulo.id_permiso_modulo == permiso_id)
                .first()
            )
        except SQLAlchemyError as e:
            raise RepositoryError("Error al obtener el permiso de módulo.") from e

    def get_by_rol_id(self, rol_id: int) -> List[PermisoModulo]:
        """Obtiene todos los permisos de un rol"""
        try:
            return (
                self.db.query(PermisoModulo)
                .options(joinedload(PermisoModulo.rol))
                .filter(PermisoModulo.id_rol == rol_id)
                .filter(PermisoModulo.is_active == True)
                .all()
            )
        except SQLAlchemyError as e:
            raise RepositoryError("Error al obtener los permisos de módulo.") from e

    def get_by_rol_and_modulo(self, rol_id: int, modulo: ModuloEnum) -> Optional[PermisoModulo]:
        """Obtiene un permiso específico de un rol para un módulo"""
        try:
            return (
                self.db.query(PermisoModulo)
                .filter(PermisoModulo.id_rol == rol_id)
                .filter(PermisoModulo.modulo == modulo)
                .filter(PermisoModulo.is_active == True)
                .first()
            )
        except SQLAlchemyError as e:
            raise RepositoryError("Error al obtener el permiso de módulo.") from e

    def create(self, permiso_data: PermisoModuloCreate) -> PermisoModulo:
        """Crea un nuevo permiso de módulo"""
        # Convertir lista de enums a lista de strings para JSON
        permisos_json = [p.value for p in permiso_data.permisos]
        
        db_permiso = PermisoModulo(
            id_rol=permiso_data.id_rol,
            modulo=permiso_data.modulo,
            permisos=permisos_json,
            ruta=permiso_data.ruta,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        
        try:
            self.db.add(db_permiso)
            self.db.commit()
            self.db.refresh(db_permiso)
            
            # Cargar la relación con el rol
            return (
                self.db.query(PermisoModulo)
                .options(joinedload(PermisoModulo.rol))
                .filter(PermisoModulo.id_permiso_modulo == db_permiso.id_permiso_modulo)
                .first()
            )
        except SQLAlchemyError as e:
            raise RepositoryError("Error al crear el permiso de módulo.") from e

    def update(self, permiso_id: int, permiso_data: PermisoModuloUpdate) -> Optional[PermisoModulo]:
        """Actualiza un permiso de módulo existente"""
        try:
            db_permiso = self.db.query(PermisoModulo).filter(
                PermisoModulo.id_permiso_modulo == permiso_id
            ).first()
        except SQLAlchemyError as e:
            raise RepositoryError("Error al actualizar el permiso de módulo.") from e
        
        if not db_permiso:
            return None

        # Actualizar solo los campos proporcionados
        update_data = permiso_data.model_dump(exclude_unset=True)
        
        # Convertir permisos a JSON si se proporcionan
        if "permisos" in update_data:
            update_data["permisos"] = [p.value for p in update_data["permisos"]]
        
        update_data["updated_at"] = datetime.now()
        
        for field, value in update_data.items():
            if hasattr(db_permiso, field):
                setattr(db_permiso, field, value)

        try:
            self.db.commit()
            self.db.refresh(db_permiso)
            
            # Cargar la relación con el rol
            return (
                self.db.query(PermisoModulo)
                .options(joinedload(PermisoModulo.rol))
                .filter(PermisoModulo.id_permiso_modulo == permiso_id)
                .first()
            )
        except SQLAlchemyError as e:
            raise RepositoryError("Error al actualizar el permiso de módulo.") from e

    def soft_delete(self, permiso_id: int) -> Optional[PermisoModulo]:
        """Desactiva un permiso de módulo (soft delete)"""
        try:
            db_permiso = self.db.query(PermisoModulo).filter(
                PermisoModulo.id_permiso_modulo == permiso_id
            ).first()
        except SQLAlchemyError as e:
            raise RepositoryError("Error al desactivar el permiso de módulo.") from e
        
        if not db_permiso:
            return None

        db_permiso.is_active = False
        db_permiso.updated_at = datetime.now()
        
        try:
            self.db.commit()
            self.db.refresh(db_permiso)
            
            return db_permiso
        except SQLAlchemyError as e:
            raise RepositoryError("Error al desactivar el permiso de módulo.") from e

    def delete_by_rol_id(self, rol_id: int) -> bool:
        """Elimina todos los permisos de un rol"""
        try:
            self.db.query(PermisoModulo).filter(
                PermisoModulo.id_rol == rol_id
            ).update({
                "is_active": False,
                "updated_at": datetime.now()
            })
            
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError("Error al eliminar los permisos de un rol.") from e
