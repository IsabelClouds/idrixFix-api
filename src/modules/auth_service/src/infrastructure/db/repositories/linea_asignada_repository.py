from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from datetime import datetime

from src.modules.auth_service.src.application.ports.lineas_asignadas import ILineaAsignadaRepository
from src.modules.auth_service.src.infrastructure.db.models import UsuarioLineaAsignada
from src.shared.exceptions import AlreadyExistsError, RepositoryError, NotFoundError

class LineaAsignadaRepository(ILineaAsignadaRepository):
    def __init__(self, db: Session):
        self.db = db  # Esta es la sesión de la DB interna (auth)

    def get_by_usuario_id(self, id_usuario: int) -> List[UsuarioLineaAsignada]:
        try:
            return (
                self.db.query(UsuarioLineaAsignada)
                .filter(UsuarioLineaAsignada.id_usuario == id_usuario)
                .all()
            )
        except SQLAlchemyError as e:
            raise RepositoryError("Error al obtener líneas asignadas.") from e

    def verificar_existencia(self, id_usuario: int, id_linea_externa: int) -> bool:
        try:
            return (
                self.db.query(UsuarioLineaAsignada)
                .filter(
                    UsuarioLineaAsignada.id_usuario == id_usuario,
                    UsuarioLineaAsignada.id_linea_externa == id_linea_externa
                )
                .first() is not None
            )
        except SQLAlchemyError as e:
            raise RepositoryError("Error al verificar existencia de línea.") from e

    def asignar(self, id_usuario: int, id_linea_externa: int) -> UsuarioLineaAsignada:
        if self.verificar_existencia(id_usuario, id_linea_externa):
            raise AlreadyExistsError("Esta línea ya está asignada al usuario.")
            
        db_asignacion = UsuarioLineaAsignada(
            id_usuario=id_usuario,
            id_linea_externa=id_linea_externa,
            created_at=datetime.now()
        )
        try:
            self.db.add(db_asignacion)
            self.db.commit()
            self.db.refresh(db_asignacion)
            return db_asignacion
        except IntegrityError as e:
            self.db.rollback()
            raise AlreadyExistsError("Asignación duplicada.") from e
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError("Error al asignar la línea.") from e

    def remover(self, id_usuario: int, id_linea_externa: int) -> bool:
        try:
            db_asignacion = (
                self.db.query(UsuarioLineaAsignada)
                .filter(
                    UsuarioLineaAsignada.id_usuario == id_usuario,
                    UsuarioLineaAsignada.id_linea_externa == id_linea_externa
                )
                .first()
            )
            
            if not db_asignacion:
                raise NotFoundError("Asignación no encontrada.")
                
            self.db.delete(db_asignacion)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError("Error al remover la línea.") from e