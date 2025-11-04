from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

# Importa el puerto (interfaz) que este repositorio implementa
from src.modules.auth_service.src.application.ports.turno_externo_repository import ITurnoExternaRepository
# Importa la entidad de dominio (dataclass)
from src.modules.auth_service.src.domain.entities import TurnoExterno
# Importa el modelo ORM de la DB externa
from src.modules.auth_service.src.infrastructure.db.models import TurnoORM
# (Ajusta la ruta a TurnoORM si es diferente)

from src.shared.exceptions import RepositoryError

class TurnoExternaRepository(ITurnoExternaRepository):
    
    def __init__(self, db: Session):
        # ¡Importante! Esta 'db' es la sesión de la DB externa (main)
        self.db = db

    def get_by_id(self, id_turno: int) -> Optional[TurnoExterno]:
        """
        Busca un turno por ID y lo mapea a la entidad de dominio.
        """
        try:
            turno_orm = (
                self.db.query(TurnoORM)
                .filter(TurnoORM.TURN_ID == id_turno)
                .first()
            )
        except SQLAlchemyError as e:
            raise RepositoryError(f"Error al buscar turno externo con id={id_turno}") from e
        
        if not turno_orm:
            return None
            
        # Mapeo de ORM (Infraestructura) a Entidad (Dominio)
        return TurnoExterno(
            id_turno=turno_orm.TURN_ID,
            nombre=turno_orm.TURN_NOMBRE,
            estado=turno_orm.TURN_ESTADO
        )

    def exists_by_id(self, id_turno: int) -> bool:
        """
        Verifica si un turno existe y está activo (compatible con SQL Server).
        """
        try:
            turno_encontrado = (
                self.db.query(TurnoORM.TURN_ID) 
                .filter(
                    TurnoORM.TURN_ID == id_turno,
                    TurnoORM.TURN_ESTADO == "ACTIVO" 
                )
                .first()
            )
            return turno_encontrado is not None
        except SQLAlchemyError as e:
            raise RepositoryError(f"Error al verificar turno externo con id={id_turno}") from e

    def get_all_active(self) -> List[TurnoExterno]:
        """
        Obtiene todos los turnos externos que están activos, ordenados por nombre.
        """
        try:
            turnos_orm = (
                self.db.query(TurnoORM)
                .filter(TurnoORM.TURN_ESTADO == "ACTIVO")
                .order_by(TurnoORM.TURN_NOMBRE.asc())
                .all()
            )
            
            # Mapear de ORM a Entidades de Dominio
            return [
                TurnoExterno(
                    id_turno=turno.TURN_ID,
                    nombre=turno.TURN_NOMBRE,
                    estado=turno.TURN_ESTADO
                )
                for turno in turnos_orm
            ]
        except SQLAlchemyError as e:
            raise RepositoryError("Error al obtener todos los turnos activos.") from e