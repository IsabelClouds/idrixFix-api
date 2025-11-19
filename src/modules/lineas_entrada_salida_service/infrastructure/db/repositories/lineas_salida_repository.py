import logging
from typing import Tuple, List, Optional

from sqlalchemy import func, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.modules.lineas_entrada_salida_service.application.ports.lineas_salida import ILineasSalidaRepository
from src.modules.lineas_entrada_salida_service.domain.entities import LineasSalida
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.lineas_filters import LineasFilters
from src.modules.lineas_entrada_salida_service.infrastructure.db.models import LineaUnoSalidaORM, LineaDosSalidaORM, \
    LineaTresSalidaORM, LineaCuatroSalidaORM, LineaCincoSalidaORM, LineaSeisSalidaORM
from src.shared.exceptions import RepositoryError

LINEA_ORM_MAPPER = {
    1: LineaUnoSalidaORM,
    2: LineaDosSalidaORM,
    3: LineaTresSalidaORM,
    4: LineaCuatroSalidaORM,
    5: LineaCincoSalidaORM,
    6: LineaSeisSalidaORM
}

class LineasSalidaRepository(ILineasSalidaRepository):
    def __init__(self, db: Session):
        self.db = db

    def _get_orm_model(self, linea_num: int):
        orm_model = LINEA_ORM_MAPPER.get(linea_num)
        if not orm_model:
            raise RepositoryError(f"Línea salida {linea_num} no válida o no implementada.")
        return orm_model

    def _apply_filters(self, query, filters: LineasFilters, orm_model):
        conditions = []

        if filters.fecha_inicial and filters.fecha_final:
            conditions.append(
                orm_model.fecha_p.between(filters.fecha_inicial, filters.fecha_final)
            )

        if conditions:
            query = query.filter(and_(*conditions))

        return query

    def count_by_filters(self, filters: LineasFilters, linea_num: int) -> int:
        orm_model = self._get_orm_model(linea_num)
        try:
            query = self.db.query(func.count(orm_model.id))

            query = self._apply_filters(query, filters, orm_model)

            return query.scalar() or 0
        except SQLAlchemyError as e:
            raise RepositoryError(f"Error al contar las lineas salida {linea_num}.") from e

    def get_by_id(self, linea_id: int, linea_num: int) -> Optional[LineasSalida]:
        orm_model = self._get_orm_model(linea_num)
        try:
            linea_orm = (
                self.db.query(orm_model)
                .filter(orm_model.id == linea_id)
                .first()
            )
            if not linea_orm:
                return None
            return LineasSalida(
                    id=linea_orm.id,
                    fecha_p=linea_orm.fecha_p,
                    fecha=linea_orm.fecha,
                    peso_kg=linea_orm.peso_kg,
                    codigo_bastidor=linea_orm.codigo_bastidor,
                    p_lote=linea_orm.p_lote,
                    codigo_parrilla=linea_orm.codigo_parrilla,
                    codigo_obrero=linea_orm.codigo_obrero,
                    guid=linea_orm.guid
                )
        except SQLAlchemyError as e:
            raise RepositoryError("Error al consultar la linea entrada.") from e

    def get_paginated_by_filters(self, filters: LineasFilters, page: int, page_size: int, linea_num: int) -> Tuple[
        List[LineasSalida], int]:
        orm_model = self._get_orm_model(linea_num)

        try:
            total_records = self.count_by_filters(filters, linea_num)

            if total_records == 0:
                return [], 0

            base_query = self.db.query(orm_model)
            data_query = self._apply_filters(base_query, filters, orm_model)

            data_query = data_query.order_by(orm_model.fecha_p.desc())

            offset = (page - 1) * page_size
            data_query = data_query.limit(page_size).offset(offset)

            lineas_entrada_data = data_query.all()

            domain_entities = [
                LineasSalida(
                    id=linea.id,
                    fecha_p=linea.fecha_p,
                    fecha=linea.fecha,
                    peso_kg=linea.peso_kg,
                    codigo_bastidor=linea.codigo_bastidor,
                    p_lote=linea.p_lote,
                    codigo_parrilla=linea.codigo_parrilla,
                    codigo_obrero=linea.codigo_obrero,
                    guid=linea.guid
                )
                for linea in lineas_entrada_data
            ]

            return domain_entities, total_records
        except SQLAlchemyError as e:
            logging.error(f"FALLO DE DB DETALLADO: {e}")
            raise RepositoryError("Error al obtener todas las líneas entrada.") from e

    #TODO hacer el update

    # def update(self, linea_id: int, linea_entrada_data: LineasEntradaUpdate, linea_num: int) -> Optional[LineasEntrada]:
    #     orm_model = self.db.query(self._get_orm_model(linea_num)).get(linea_id)
    #     if not orm_model:
    #         raise NotFoundError(f"Producción de linea entrada con id={linea_id} no encontrado.")
    #
    #     update_data = linea_entrada_data.model_dump(exclude_unset=True)
    #     for key, value in update_data.items():
    #         setattr(orm_model, key, value)
    #
    #     try:
    #         self.db.commit()
    #         self.db.refresh(orm_model)
    #         return LineasEntrada(
    #                 id=orm_model.id,
    #                 fecha_p=orm_model.fecha_p,
    #                 fecha=orm_model.fecha,
    #                 peso_kg=orm_model.peso_kg,
    #                 turno=orm_model.turno,
    #                 codigo_secuencia=orm_model.codigo_secuencia,
    #                 codigo_parrilla=orm_model.codigo_parrilla,
    #                 p_lote=orm_model.p_lote,
    #                 hora_inicio=orm_model.hora_inicio,
    #                 guid=orm_model.guid
    #             )
    #     except SQLAlchemyError as e:
    #         self.db.rollback()
    #         raise RepositoryError("Error al actualizar la producción de la linea entrada.") from e