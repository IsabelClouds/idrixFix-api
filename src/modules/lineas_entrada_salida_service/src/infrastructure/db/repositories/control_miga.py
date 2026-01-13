from typing import Optional

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

    def create(self, linea_num: int, registro: int, p_miga: float, porcentaje: float) -> ControlMiga:

        try:
            db_miga = ControlMigaOrm(
                linea = linea_num,
                registro = registro,
                p_miga = p_miga,
                porcentaje = porcentaje
            )

            self.db.add(db_miga)
            self.db.commit()
            self.db.refresh(db_miga)

            return ControlMiga(
                id = db_miga.id,
                linea = db_miga.linea,
                registro = db_miga.registro,
                p_miga = db_miga.p_miga,
                porcentaje = db_miga.porcentaje
            )

        except SQLAlchemyError as e:
            self.db.rollback()
            logging.error("error en repositorio")
            raise RepositoryError("Error al crear la tara.") from e

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

            return ControlMiga(
                id=miga_orm.id,
                linea=miga_orm.linea,
                registro=miga_orm.registro,
                p_miga=miga_orm.p_miga,
                porcentaje=miga_orm.porcentaje
            )
        except SQLAlchemyError as e:
            raise RepositoryError("Error al consultar la miga.") from e


    def update(self, id: int, p_miga: float, porcentaje: float) -> Optional[ControlMiga]:
        miga_orm = self.db.query(ControlMigaOrm).get(id)

        if miga_orm is None:
            raise NotFoundError("Miga no encontrada.")

        miga_orm.p_miga = p_miga
        miga_orm.porcentaje = porcentaje

        try:
            self.db.commit()
            self.db.refresh(miga_orm)
            return ControlMiga(
                id=miga_orm.id,
                linea=miga_orm.linea,
                registro=miga_orm.registro,
                p_miga=miga_orm.p_miga,
                porcentaje=miga_orm.porcentaje
            )
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError("Error al actualizar la miga.") from e
