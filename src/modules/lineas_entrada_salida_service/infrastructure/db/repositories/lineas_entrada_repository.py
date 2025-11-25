import logging
from typing import List, Tuple, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from src.modules.lineas_entrada_salida_service.application.ports.lineas_entrada import ILineasEntradaRepository
from src.modules.lineas_entrada_salida_service.domain.entities import LineasEntrada
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.lineas_entrada import LineasEntradaUpdate
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.lineas_filters import \
    LineasFilters
from src.modules.lineas_entrada_salida_service.infrastructure.db.models import LineaUnoEntradaORM, LineaDosEntradaORM, \
    LineaTresEntradaORM, LineaCuatroEntradaORM, LineaCincoEntradaORM, LineaSeisEntradaORM
from src.shared.exceptions import RepositoryError, NotFoundError

LINEA_ORM_MAPPER = {
    1: LineaUnoEntradaORM,
    2: LineaDosEntradaORM,
    3: LineaTresEntradaORM,
    4: LineaCuatroEntradaORM,
    5: LineaCincoEntradaORM,
    6: LineaSeisEntradaORM
}

class LineasEntradaRepository(ILineasEntradaRepository):
    def __init__(self, db: Session):
        self.db = db

    def _get_orm_model(self, linea_num: int):
        orm_model = LINEA_ORM_MAPPER.get(linea_num)
        if not orm_model:
            raise RepositoryError(f"Línea entrada {linea_num} no válida o no implementada.")
        return orm_model

    def _apply_filters(self, query, filters: LineasFilters, orm_model):
        conditions = []

        if filters.fecha:
            conditions.append(
                orm_model.fecha_p == filters.fecha
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
            raise RepositoryError(f"Error al contar las lineas entrada {linea_num}.") from e

    def get_by_id(self, linea_id: int, linea_num: int) -> Optional[LineasEntrada]:
        orm_model = self._get_orm_model(linea_num)
        try:
            linea_orm = (
                self.db.query(orm_model)
                .filter(orm_model.id == linea_id)
                .first()
            )
            if not linea_orm:
                return None
            return LineasEntrada(
                id=linea_orm.id,
                fecha_p=linea_orm.fecha_p,
                fecha=linea_orm.fecha,
                peso_kg=linea_orm.peso_kg,
                turno=linea_orm.turno,
                codigo_secuencia=linea_orm.codigo_secuencia,
                codigo_parrilla=linea_orm.codigo_parrilla,
                p_lote=linea_orm.p_lote,
                hora_inicio=linea_orm.hora_inicio,
                guid=linea_orm.guid
            )
        except SQLAlchemyError as e:
            raise RepositoryError("Error al consultar la linea entrada.") from e

    def get_paginated_by_filters(self, filters: LineasFilters, page: int, page_size: int, linea_num: int) -> Tuple[
        List[LineasEntrada], int]:
        orm_model = self._get_orm_model(linea_num)

        try:
            total_records = self.count_by_filters(filters, linea_num)

            if total_records == 0:
                return [], 0

            base_query = self.db.query(orm_model)
            data_query = self._apply_filters(base_query, filters, orm_model)

            data_query = data_query.order_by(orm_model.fecha_p.desc(), orm_model.hora_inicio.desc())

            offset = (page - 1) * page_size
            data_query = data_query.limit(page_size).offset(offset)

            lineas_entrada_data = data_query.all()

            domain_entities = [
                LineasEntrada(
                    id=linea.id,
                    fecha_p=linea.fecha_p,
                    fecha=linea.fecha,
                    peso_kg=linea.peso_kg,
                    turno=linea.turno,
                    codigo_secuencia=linea.codigo_secuencia,
                    codigo_parrilla=linea.codigo_parrilla,
                    p_lote=linea.p_lote,
                    hora_inicio=linea.hora_inicio,
                    guid=linea.guid
                )
                for linea in lineas_entrada_data
            ]

            return domain_entities, total_records
        except SQLAlchemyError as e:
            logging.error(f"FALLO DE DB DETALLADO: {e}")
            raise RepositoryError("Error al obtener todas las líneas entrada.") from e

    def update(self, linea_id: int, linea_entrada_data: LineasEntradaUpdate, linea_num: int) -> Optional[LineasEntrada]:
        orm_model = self.db.query(self._get_orm_model(linea_num)).get(linea_id)
        if not orm_model:
            raise NotFoundError(f"Producción de linea entrada con id={linea_id} no encontrado.")

        update_data = linea_entrada_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(orm_model, key, value)

        try:
            self.db.commit()
            self.db.refresh(orm_model)
            return LineasEntrada(
                id=orm_model.id,
                fecha_p=orm_model.fecha_p,
                fecha=orm_model.fecha,
                peso_kg=orm_model.peso_kg,
                turno=orm_model.turno,
                codigo_secuencia=orm_model.codigo_secuencia,
                codigo_parrilla=orm_model.codigo_parrilla,
                p_lote=orm_model.p_lote,
                hora_inicio=orm_model.hora_inicio,
                guid=orm_model.guid
            )
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError("Error al actualizar la producción de la linea entrada.") from e

    def remove(self, linea_id: int, linea_num: int) -> bool:
        try:
            linea_orm = self.db.query(self._get_orm_model(linea_num)).get(linea_id)
            if not linea_orm:
                raise NotFoundError(f"Producción de linea entrada con id={linea_id} no encontrado.")
            self.db.delete(linea_orm)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logging.error(f"FALLO DE DB DETALLADO: {e}")
            raise RepositoryError("Error al elimar linea entrada.") from e

    def update_codigo_parrilla(self, linea_id: int, linea_num: int, valor: str) -> Optional[LineasEntrada]:
        try:
            linea_orm = self.db.query(self._get_orm_model(linea_num)).get(linea_id)
            if linea_orm is None:
                raise NotFoundError(f"Producción de linea entrada con id={linea_id} no encontrado.")

            linea_orm.codigo_parrilla = valor
            self.db.commit()
            self.db.refresh(linea_orm)

            return LineasEntrada(
                id=linea_orm.id,
                fecha_p=linea_orm.fecha_p,
                fecha=linea_orm.fecha,
                peso_kg=linea_orm.peso_kg,
                turno=linea_orm.turno,
                codigo_secuencia=linea_orm.codigo_secuencia,
                codigo_parrilla=linea_orm.codigo_parrilla,
                p_lote=linea_orm.p_lote,
                hora_inicio=linea_orm.hora_inicio,
                guid=linea_orm.guid
            )
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError("Error al actualizar el código de parrilla de la línea entrada.") from e
