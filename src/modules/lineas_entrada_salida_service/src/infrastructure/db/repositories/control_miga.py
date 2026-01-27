import datetime
from typing import Optional, List

from src.modules.lineas_entrada_salida_service.src.application.ports.control_miga import IControlMigaRepository
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from src.modules.lineas_entrada_salida_service.src.domain.entities import ControlMiga
from src.modules.lineas_entrada_salida_service.src.infrastructure.db.models import ControlMigaOrm
from src.shared.exceptions import RepositoryError, NotFoundError


class ControlMigaRepository(IControlMigaRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_domain(self, miga_orm: ControlMigaOrm) -> ControlMiga:
        """Convierte un objeto ORM de SQLAlchemy a una entidad de dominio."""
        return ControlMiga(
            id=miga_orm.id,
            linea=miga_orm.linea,
            registro=miga_orm.registro,
            p_miga=miga_orm.p_miga,
            porcentaje=miga_orm.porcentaje,
            created_at=miga_orm.created_at,
            updated_at=miga_orm.updated_at
        )

    def create(self, linea_num: int, registro: int, p_miga: float, porcentaje: float) -> ControlMiga:

        try:
            db_miga = ControlMigaOrm(
                linea=linea_num,
                registro=registro,
                p_miga=p_miga,
                porcentaje=porcentaje,
                created_at=datetime.datetime.now()
            )

            self.db.add(db_miga)
            self.db.commit()
            self.db.refresh(db_miga)

            return self._to_domain(db_miga)

        except SQLAlchemyError as e:
            self.db.rollback()
            logging.error("error en repositorio")
            raise RepositoryError("Error al crear la tara.") from e

    def get_by_registros_bulk(self, linea_num: int, registros: list[int]) -> List[ControlMiga]:
        try:
            migas_orm = (
                self.db.query(ControlMigaOrm)
                .filter(
                    ControlMigaOrm.linea == linea_num,
                    ControlMigaOrm.registro.in_(registros)
                )
                .all()
            )
            return [self._to_domain(m) for m in migas_orm]
        except SQLAlchemyError as e:
            raise RepositoryError("Error al consultar migas en bloque") from e

    def update(self, id: int, p_miga: float, porcentaje: float) -> Optional[ControlMiga]:
        miga_orm = self.db.query(ControlMigaOrm).get(id)

        if miga_orm is None:
            raise NotFoundError("Miga no encontrada.")

        miga_orm.p_miga = p_miga
        miga_orm.porcentaje = porcentaje
        miga_orm.updated_at = datetime.datetime.now()

        try:
            self.db.commit()
            self.db.refresh(miga_orm)
            return self._to_domain(miga_orm)
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError("Error al actualizar la miga.") from e

    def get_by_registro(self, linea_num: int, registro: int) -> Optional[ControlMiga]:
        try:
            miga_orm = (
                self.db.query(ControlMigaOrm)
                .filter(
                    ControlMigaOrm.linea == linea_num,
                    ControlMigaOrm.registro == registro
                )
                .first()
            )

            if not miga_orm:
                return None

            return self._to_domain(miga_orm)

        except SQLAlchemyError as e:
          raise RepositoryError("Error al consultar la miga.") from e
