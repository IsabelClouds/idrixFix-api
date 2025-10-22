from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

# Importa el puerto (interfaz)
from src.modules.auth_service.src.application.ports.linea_externa import ILineaExternaRepository
# Importa la entidad de dominio
from src.modules.auth_service.src.domain.entities import LineaExterna
# Importa el modelo ORM de la DB externa
from src.modules.auth_service.src.infrastructure.db.models import LineaORM 

from src.shared.exceptions import RepositoryError

class LineaExternaRepository(ILineaExternaRepository):
    
    def __init__(self, db: Session):
        self.db = db

    def _get_orm_by_id(self, id_linea: int) -> Optional[LineaORM]:
        """Helper para obtener el modelo ORM crudo"""
        try:
            return (
                self.db.query(LineaORM)
                .filter(LineaORM.LINE_ID == id_linea)
                .first()
            )
        except SQLAlchemyError as e:
            raise RepositoryError(f"Error al buscar línea externa con id={id_linea}") from e

    def get_by_id(self, id_linea: int) -> Optional[LineaExterna]:
        """
        Busca una línea por ID y la mapea a la entidad de dominio.
        """
        linea_orm = self._get_orm_by_id(id_linea)
        
        if not linea_orm:
            return None
            
        # Mapeo de ORM (Infraestructura) a Entidad (Dominio)
        return LineaExterna(
            id_linea=linea_orm.LINE_ID,
            nombre=linea_orm.LINE_NOMBRE,
            estado=linea_orm.LINE_ESTADO,
            id_planta=linea_orm.LINE_PLANTA
        )

    def exists_by_id(self, id_linea: int) -> bool:
        """
        Verifica si una línea existe y está activa.
        """
        try:
            linea_encontrada = (
                self.db.query(LineaORM.LINE_ID)
                .filter(
                    LineaORM.LINE_ID == int(id_linea),
                    LineaORM.LINE_ESTADO == "ACTIVO"
                )
                .first()
            )
            return linea_encontrada is not None
        except SQLAlchemyError as e:
            raise RepositoryError(f"Error al verificar línea externa con id={id_linea}") from e