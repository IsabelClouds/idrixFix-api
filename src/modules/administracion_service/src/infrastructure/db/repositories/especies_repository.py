from typing import Optional, List, Tuple

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.modules.administracion_service.src.application.ports.especies import IEspeciesRepository
from src.modules.administracion_service.src.domain.entities import Especie
from src.modules.administracion_service.src.infrastructure.api.schemas.especies import EspeciesRequest, \
    EspeciesPaginated
from src.modules.administracion_service.src.infrastructure.db.models import EspeciesORM
from src.shared.exceptions import RepositoryError, NotFoundError


class EspeciesRepository(IEspeciesRepository):
    def __init__(self, db: Session):
        self.db = db

    def _count(self) -> int:
        try:
            query = self.db.query(func.count(EspeciesORM.especie_id))

            return query.scalar() or 0
        except SQLAlchemyError as e:
            raise RepositoryError(f"Error al contar .") from e

    def get_all_paginated(self, pagination: EspeciesPaginated) -> Tuple[
        List[Especie], int]:
        try:
            total_records = self._count()
            if total_records == 0:
                return [], 0

            base_query = self.db.query(EspeciesORM)
            base_query = base_query.order_by(EspeciesORM.especie_id.desc())

            offset = (pagination.page - 1) * pagination.page_size
            data_query = base_query.limit(pagination.page_size).offset(offset)

            especies_orm = data_query.all()

            domain_entities =[
                Especie(
                    especie_id=e.especie_id,
                    especie_nombre=e.especie_nombre,
                    especie_familia=e.especie_familia,
                    especie_rend_normal=e.especie_rend_normal,
                    especie_merm_coccion=e.especie_merm_coccion,
                    especie_kilos_horas=e.especie_kilos_horas,
                    especie_piezas=e.especie_piezas,
                    especie_peso_promed=e.especie_peso_promed,
                    especie_peso_crudo=e.especie_peso_crudo,
                    especie_rendimiento=e.especie_rendimiento,
                    especie_time_limpieza=e.especie_time_limpieza,
                    especies_kilos_horas_media=e.especies_kilos_horas_media,
                    especies_kilos_horas_doble=e.especies_kilos_horas_doble
                )
                for e in especies_orm
            ]

            return domain_entities, total_records
        except SQLAlchemyError as e:
            raise RepositoryError("Error al obtener las especies") from e

    def get_by_id(self, id: int) -> Optional[Especie]:
        try:
            especie_orm = (
                self.db.query(EspeciesORM)
                .filter(EspeciesORM.especie_id == id)
                .first()
            )
            if not especie_orm:
                return None
            return Especie(
                especie_id=especie_orm.especie_id,
                especie_nombre=especie_orm.especie_nombre,
                especie_familia=especie_orm.especie_familia,
                especie_rend_normal=especie_orm.especie_rend_normal,
                especie_merm_coccion=especie_orm.especie_merm_coccion,
                especie_kilos_horas=especie_orm.especie_kilos_horas,
                especie_piezas=especie_orm.especie_piezas,
                especie_peso_promed=especie_orm.especie_peso_promed,
                especie_peso_crudo=especie_orm.especie_peso_crudo,
                especie_rendimiento=especie_orm.especie_rendimiento,
                especie_time_limpieza=especie_orm.especie_time_limpieza,
                especies_kilos_horas_media=especie_orm.especies_kilos_horas_media,
                especies_kilos_horas_doble=especie_orm.especies_kilos_horas_doble
            )
        except SQLAlchemyError as e:
            raise RepositoryError("Error al consultar la especie.") from e

    def exists_by_id(self, id: int):
        try:
            especie_orm = (
                self.db.query(EspeciesORM.especie_id)
                .filter(
                    EspeciesORM.especie_id == id
                )
                .first()
            )
            return especie_orm is not None
        except SQLAlchemyError as e:
            raise RepositoryError("Error al consultar existencia de la especie.") from e

    def exists_by_nombre(self, nombre: str):
        try:
            especie_orm = (
                self.db.query(EspeciesORM.especie_id)
                .filter(EspeciesORM.especie_nombre == nombre)
                .first()
            )
            return especie_orm is not None
        except SQLAlchemyError as e:
            raise RepositoryError("Error al consultar existencia de la especie.") from e

    def create(self, data: EspeciesRequest) -> Especie:
        try:
            especie_orm = EspeciesORM(
                especie_nombre=data.especie_nombre,
                especie_familia=data.especie_familia,
                especie_kilos_horas=data.especie_kilos_horas,
                especies_kilos_horas_media=data.especies_kilos_horas_media,
                especies_kilos_horas_doble=data.especies_kilos_horas_doble
            )
            self.db.add(especie_orm)
            self.db.commit()
            self.db.refresh(especie_orm)
            return Especie(
                especie_id=especie_orm.especie_id,
                especie_nombre=especie_orm.especie_nombre,
                especie_familia=especie_orm.especie_familia,
                especie_rend_normal=especie_orm.especie_rend_normal,
                especie_merm_coccion=especie_orm.especie_merm_coccion,
                especie_kilos_horas=especie_orm.especie_kilos_horas,
                especie_piezas=especie_orm.especie_piezas,
                especie_peso_promed=especie_orm.especie_peso_promed,
                especie_peso_crudo=especie_orm.especie_peso_crudo,
                especie_rendimiento=especie_orm.especie_rendimiento,
                especie_time_limpieza=especie_orm.especie_time_limpieza,
                especies_kilos_horas_media=especie_orm.especies_kilos_horas_media,
                especies_kilos_horas_doble=especie_orm.especies_kilos_horas_doble
            )
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError("Error al crear la especie.") from e

    def update(self, data: EspeciesRequest, id: int):
        especie_orm = self.db.query(EspeciesORM).get(id)
        if especie_orm is None:
            raise NotFoundError("Especie no en contrada")

        updated_data = data.model_dump(exclude_unset=True)
        for k, v in updated_data.items():
            setattr(especie_orm, k, v)

        try:
            self.db.commit()
            self.db.refresh(especie_orm)
            return Especie(
                especie_id=especie_orm.especie_id,
                especie_nombre=especie_orm.especie_nombre,
                especie_familia=especie_orm.especie_familia,
                especie_rend_normal=especie_orm.especie_rend_normal,
                especie_merm_coccion=especie_orm.especie_merm_coccion,
                especie_kilos_horas=especie_orm.especie_kilos_horas,
                especie_piezas=especie_orm.especie_piezas,
                especie_peso_promed=especie_orm.especie_peso_promed,
                especie_peso_crudo=especie_orm.especie_peso_crudo,
                especie_rendimiento=especie_orm.especie_rendimiento,
                especie_time_limpieza=especie_orm.especie_time_limpieza,
                especies_kilos_horas_media=especie_orm.especies_kilos_horas_media,
                especies_kilos_horas_doble=especie_orm.especies_kilos_horas_doble
            )
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError("Error al actualizar la especie.") from e
