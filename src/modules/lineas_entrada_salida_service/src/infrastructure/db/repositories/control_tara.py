import logging
from typing import Optional, List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.modules.lineas_entrada_salida_service.src.application.ports.control_tara import IControlTaraRepository
from src.modules.lineas_entrada_salida_service.src.infrastructure.api.schemas.control_tara import TaraCreate
from src.modules.lineas_entrada_salida_service.src.infrastructure.db.models import ControlTaraOrm
from src.modules.lineas_entrada_salida_service.src.domain.entities import ControlTara
from src.shared.exceptions import RepositoryError, NotFoundError


class ControlTaraRepository(IControlTaraRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[ControlTara]:
        try:
            taras_orm = (
                self.db.query(ControlTaraOrm)
                .filter(ControlTaraOrm.is_active == True)
                .all()
            )

            return [
                ControlTara(
                    id=t.id,
                    nombre=t.nombre,
                    descripcion=t.descripcion,
                    peso_kg=t.peso_kg,
                    is_active=t.is_active,
                    is_principal=t.is_principal
                )
                for t in taras_orm
            ]

        except SQLAlchemyError as e:
            raise RepositoryError("Error al obtener las taras.") from e

    def create(self, tara_data: TaraCreate) -> ControlTara:
        try:
            db_tara = ControlTaraOrm(
                nombre = tara_data.nombre,
                descripcion = tara_data.descripcion,
                peso_kg=tara_data.peso_kg
            )

            self.db.add(db_tara)
            self.db.commit()
            self.db.refresh(db_tara)
            return ControlTara(
                id=db_tara.id,
                nombre=db_tara.nombre,
                descripcion=db_tara.descripcion,
                peso_kg=db_tara.peso_kg,
                is_active=db_tara.is_active,
                is_principal=db_tara.is_principal
            )
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
                nombre=tara_orm.nombre,
                descripcion=tara_orm.descripcion,
                peso_kg=tara_orm.peso_kg,
                is_active=tara_orm.is_active,
                is_principal=tara_orm.is_principal
            )
        except SQLAlchemyError as e:
            raise RepositoryError("Error al consultar la tara.") from e

    def soft_delete(self, tara_id: int) -> bool:
        try:
            tara_orm = (
                self.db.query(ControlTaraOrm)
                .filter(ControlTaraOrm.id == tara_id)
                .first()
            )

            if tara_orm is None:
                raise NotFoundError(f"Tara con id={tara_id} no encontrada.")

            tara_orm.is_active = False
            self.db.commit()
            self.db.refresh(tara_orm)

            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError("Error al eliminar la tara.") from e

    def exists_by_peso_kg(self, peso_kg_tara: float) -> bool:
        try:
            tara_orm = (
                self.db.query(ControlTaraOrm.id)
                .filter(
                    ControlTaraOrm.peso_kg == peso_kg_tara,
                    ControlTaraOrm.is_active == True
                )
                .first()
            )
            return tara_orm is not None
        except SQLAlchemyError as e:
            raise RepositoryError("Error al consultar existencia de la tara.") from e

    def exists_by_nombre(self, nombre: str) -> bool:
        try:
            tara_orm = (
                self.db.query(ControlTaraOrm.id)
                .filter(
                    ControlTaraOrm.nombre == nombre,
                    ControlTaraOrm.is_active == True
                )
                .first()
            )
            return tara_orm is not None
        except SQLAlchemyError as e:
            raise RepositoryError("Error al consultar existencia de la tara.") from e

    def get_principal(self) -> Optional[ControlTara]:
        tara_orm = (
            self.db.query(ControlTaraOrm)
            .filter(ControlTaraOrm.is_principal == True)
            .first()
        )

        if tara_orm is None:
            return None

        return ControlTara(
            id=tara_orm.id,
            nombre=tara_orm.nombre,
            descripcion=tara_orm.descripcion,
            peso_kg=tara_orm.peso_kg,
            is_active=tara_orm.is_active,
            is_principal=tara_orm.is_principal
        )

    def set_principal(self, tara_id, principal: bool):
        try:
            tara_orm = self.db.query(ControlTaraOrm).get(tara_id)
            if tara_orm is None:
                raise NotFoundError(f"Tara con id={tara_id} no encontrado.")

            tara_orm.is_principal = principal

            self.db.commit()
            self.db.refresh(tara_orm)

            return ControlTara(
                id=tara_orm.id,
                nombre=tara_orm.nombre,
                descripcion=tara_orm.descripcion,
                peso_kg=tara_orm.peso_kg,
                is_active=tara_orm.is_active,
                is_principal=tara_orm.is_principal
            )

        except SQLAlchemyError as e:
            logging.error(e)
            raise RepositoryError("Error al establecer la tara principal") from e



