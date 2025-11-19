import logging
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.modules.lineas_entrada_salida_service.application.ports.control_tara import IControlTaraRepository
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.control_tara import TaraCreate
from src.modules.lineas_entrada_salida_service.infrastructure.db.models import ControlTaraOrm
from src.modules.lineas_entrada_salida_service.domain.entities import ControlTara
from src.shared.exceptions import RepositoryError


class ControlTaraRepository(IControlTaraRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, tara_data: TaraCreate) -> ControlTaraOrm:
        try:
            db_tara = ControlTaraOrm(
                peso_kg=tara_data.peso_kg
            )

            self.db.add(db_tara)
            self.db.commit()
            self.db.refresh(db_tara)
            return db_tara
        except SQLAlchemyError as e:
            self.db.rollback()
            logging.error(f"FALLO DE DB DETALLADO: {e}")
            raise RepositoryError("Error al crear la tara.") from e

    def get_by_id(self, tara_id: int) -> Optional[ControlTara]:
        try:
            tara_orm = (
                self.db.query(ControlTaraOrm)
                .filter(ControlTaraOrm.id == tara_id)
                .first()
            )
            if not tara_orm:
                return None
            return ControlTara(
                id=tara_orm.id,
                peso_kg=tara_orm.peso_kg,
                is_active=tara_orm.is_active
            )
        except SQLAlchemyError as e:
            raise RepositoryError("Error al consultar la tara.") from e