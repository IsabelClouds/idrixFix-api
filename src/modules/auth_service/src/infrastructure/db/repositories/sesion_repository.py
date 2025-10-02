from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from src.modules.auth_service.src.application.ports.sesiones import ISesionRepository
from src.modules.auth_service.src.infrastructure.api.schemas.sesiones import SesionCreate
from src.modules.auth_service.src.infrastructure.db.models import SesionUsuario
from datetime import datetime
from src.shared.exceptions import RepositoryError 
from sqlalchemy.exc import SQLAlchemyError


class SesionRepository(ISesionRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[SesionUsuario]:
        """Obtiene todas las sesiones activas"""
        try:
            return (
                self.db.query(SesionUsuario)
                .options(joinedload(SesionUsuario.usuario))
                .filter(SesionUsuario.is_active == True)
                .all()
            )
        except SQLAlchemyError as e:
            raise RepositoryError("Error al obtener las sesiones.") from e

    def get_by_id(self, sesion_id: int) -> Optional[SesionUsuario]:
        """Obtiene una sesión por ID"""
        try:
            return (
                self.db.query(SesionUsuario)
                .options(joinedload(SesionUsuario.usuario))
                .filter(SesionUsuario.id_sesion == sesion_id)
                .first()
            )
        except SQLAlchemyError as e:
            raise RepositoryError("Error al obtener la sesión.") from e

    def get_by_token(self, token: str) -> Optional[SesionUsuario]:
        """Obtiene una sesión por token"""
        try:
            return (
                self.db.query(SesionUsuario)
                .options(joinedload(SesionUsuario.usuario))
                .filter(SesionUsuario.token == token)
                .filter(SesionUsuario.is_active == True)
                .first()
            )
        except SQLAlchemyError as e:
            raise RepositoryError("Error al obtener la sesión.") from e

    def get_by_usuario_id(self, usuario_id: int) -> List[SesionUsuario]:
        """Obtiene todas las sesiones de un usuario"""
        try:
            return (
                self.db.query(SesionUsuario)
                .options(joinedload(SesionUsuario.usuario))
                .filter(SesionUsuario.id_usuario == usuario_id)
                .all()
            )
        except SQLAlchemyError as e:
            raise RepositoryError("Error al obtener las sesiones.") from e

    def get_active_by_usuario_id(self, usuario_id: int) -> List[SesionUsuario]:
        """Obtiene todas las sesiones activas de un usuario"""
        return (
            self.db.query(SesionUsuario)
            .options(joinedload(SesionUsuario.usuario))
            .filter(SesionUsuario.id_usuario == usuario_id)
            .filter(SesionUsuario.is_active == True)
            .filter(SesionUsuario.fecha_expiracion > datetime.now())
            .all()
        )

    def create(self, sesion_data: SesionCreate) -> SesionUsuario:
        """Crea una nueva sesión"""
        db_sesion = SesionUsuario(
            id_usuario=sesion_data.id_usuario,
            token=sesion_data.token,
            refresh_token=sesion_data.refresh_token,
            fecha_inicio=sesion_data.fecha_inicio,
            fecha_expiracion=sesion_data.fecha_expiracion,
            ip_address=sesion_data.ip_address,
            user_agent=sesion_data.user_agent,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        
        self.db.add(db_sesion)
        self.db.commit()
        self.db.refresh(db_sesion)
        
        return (
            self.db.query(SesionUsuario)
            .options(joinedload(SesionUsuario.usuario))
            .filter(SesionUsuario.id_sesion == db_sesion.id_sesion)
            .first()
        )

    def update(self, sesion_id: int, update_data: dict) -> Optional[SesionUsuario]:
        """Actualiza una sesión existente"""
        try:
            db_sesion = self.db.query(SesionUsuario).filter(
                SesionUsuario.id_sesion == sesion_id
            ).first()
            
            if not db_sesion:
                return None
            
            # Actualizar campos
            for field, value in update_data.items():
                if hasattr(db_sesion, field):
                    setattr(db_sesion, field, value)
            
            # Actualizar timestamp
            db_sesion.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(db_sesion)
            
            return db_sesion
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError("Error al actualizar la sesión.") from e

    def soft_delete(self, sesion_id: int) -> Optional[SesionUsuario]:
        """Desactiva una sesión (soft delete)"""
        try:
            db_sesion = self.db.query(SesionUsuario).filter(
                SesionUsuario.id_sesion == sesion_id
            ).first()
        except SQLAlchemyError as e:
            raise RepositoryError("Error al desactivar la sesión.") from e
        
        if not db_sesion:
            return None

        db_sesion.is_active = False
        db_sesion.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(db_sesion)
        
        return db_sesion

    def invalidate_by_token(self, token: str) -> Optional[SesionUsuario]:
        """Invalida una sesión por token"""
        try:
            db_sesion = self.db.query(SesionUsuario).filter(
                SesionUsuario.token == token
            ).first()
        except SQLAlchemyError as e:
            raise RepositoryError("Error al invalidar la sesión.") from e
        
        if not db_sesion:
            return None

        db_sesion.is_active = False
        db_sesion.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(db_sesion)
        
        return db_sesion

    def invalidate_all_by_usuario_id(self, usuario_id: int) -> bool:
        """Invalida  todas las sesiones de un usuario"""
        try:
            self.db.query(SesionUsuario).filter(
                SesionUsuario.id_usuario == usuario_id
            ).filter(
                SesionUsuario.is_active == True
            ).update({
                "is_active": False,
                "updated_at": datetime.now()
            })
            
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False

    def cleanup_expired_sessions(self) -> int:
        """Limpia todas las sesiones expiradas"""
        try:
            expired_count = self.db.query(SesionUsuario).filter(
                SesionUsuario.fecha_expiracion < datetime.now()
            ).filter(
                SesionUsuario.is_active == True
            ).update({
                "is_active": False,
                "updated_at": datetime.now()
            })
            
            self.db.commit()
            return expired_count
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError("Error al limpiar las sesiones expiradas.") from e
