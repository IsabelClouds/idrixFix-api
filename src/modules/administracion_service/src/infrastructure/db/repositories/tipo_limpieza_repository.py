from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.modules.administracion_service.src.application.ports.tipo_limpieza import ITipoLimpiezaRepository
from src.modules.administracion_service.src.domain.entities import TipoLimpieza
from src.modules.administracion_service.src.infrastructure.db.models import TipoLimpiezaORM
from src.shared.exceptions import RepositoryError


class TipoLimpiezaRepository(ITipoLimpiezaRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Optional[TipoLimpieza]:
        try:
            orm = (
                self.db.query(TipoLimpiezaORM)
                .filter(TipoLimpiezaORM.id_tipo_limpieza == id)
                .first()
            )
            if not orm:
                return None

            return TipoLimpieza(
                id_tipo_limpieza=orm.id_tipo_limpieza,
                nombre=orm.nombre,
                estado=orm.estado
            )
        except SQLAlchemyError as e:
            raise RepositoryError("Error al consultar el tipo limpieza.") from e