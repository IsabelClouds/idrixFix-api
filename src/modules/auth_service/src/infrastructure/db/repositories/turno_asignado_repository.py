from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from datetime import datetime

# Importa el puerto (interfaz)
from src.modules.auth_service.src.application.ports.turno_asignado_repository import ITurnoAsignadoRepository
# Importa el modelo ORM (de la DB interna)
from src.modules.auth_service.src.infrastructure.db.models import UsuarioTurnoAsignado
from src.shared.exceptions import AlreadyExistsError, RepositoryError, NotFoundError

class TurnoAsignadoRepository(ITurnoAsignadoRepository):
    
    def __init__(self, db: Session):
        self.db = db  # Esta es la sesión de la DB interna (auth)

    def get_by_usuario_id(self, id_usuario: int) -> List[UsuarioTurnoAsignado]:
        try:
            return (
                self.db.query(UsuarioTurnoAsignado)
                .filter(UsuarioTurnoAsignado.id_usuario == id_usuario)
                .all()
            )
        except SQLAlchemyError as e:
            raise RepositoryError("Error al obtener turnos asignados.") from e

    def verificar_existencia(self, id_usuario: int, id_turno_externo: int) -> bool:
        try:
            return (
                self.db.query(UsuarioTurnoAsignado)
                .filter(
                    UsuarioTurnoAsignado.id_usuario == id_usuario,
                    UsuarioTurnoAsignado.id_turno_externo == id_turno_externo
                )
                .first() is not None
            )
        except SQLAlchemyError as e:
            raise RepositoryError("Error al verificar existencia de turno.") from e

    def asignar(self, id_usuario: int, id_turno_externo: int) -> UsuarioTurnoAsignado:
        if self.verificar_existencia(id_usuario, id_turno_externo):
            raise AlreadyExistsError("Este turno ya está asignado al usuario.")
            
        db_asignacion = UsuarioTurnoAsignado(
            id_usuario=id_usuario,
            id_turno_externo=id_turno_externo,
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
            raise RepositoryError("Error al asignar el turno.") from e

    def remover(self, id_usuario: int, id_turno_externo: int) -> bool:
        try:
            db_asignacion = (
                self.db.query(UsuarioTurnoAsignado)
                .filter(
                    UsuarioTurnoAsignado.id_usuario == id_usuario,
                    UsuarioTurnoAsignado.id_turno_externo == id_turno_externo
                )
                .first()
            )
            
            if not db_asignacion:
                raise NotFoundError("Asignación de turno no encontrada.")
                
            self.db.delete(db_asignacion)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError("Error al remover el turno.") from e