import logging
from typing import Tuple, List, Optional
from sqlalchemy import func, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.modules.lineas_entrada_salida_service.src.application.ports.lineas_salida import ILineasSalidaRepository
from src.modules.lineas_entrada_salida_service.src.domain.entities import LineasSalida
from src.modules.lineas_entrada_salida_service.src.infrastructure.api.schemas.lineas_shared import LineasFilters
from src.modules.lineas_entrada_salida_service.src.infrastructure.api.schemas.lineas_salida import LineasSalidaUpdate
from src.modules.lineas_entrada_salida_service.src.infrastructure.db.models import LineaUnoSalidaORM, LineaDosSalidaORM, \
    LineaTresSalidaORM, LineaCuatroSalidaORM, LineaCincoSalidaORM, LineaSeisSalidaORM
from src.shared.exceptions import RepositoryError, NotFoundError

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

        if filters.fecha:
            conditions.append(orm_model.fecha_p == filters.fecha)

        if filters.lote:
            conditions.append(orm_model.p_lote == filters.lote)

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
            raise RepositoryError("Error al consultar la linea salida.") from e

    def get_all_by_filters(self, filters: LineasFilters, linea_num: int) -> List[LineasSalida]:
        orm_model = self._get_orm_model(linea_num)

        try:
            query = self.db.query(orm_model)
            query = self._apply_filters(query, filters, orm_model)

            query = query.order_by(orm_model.fecha_p.desc())

            lineas_orm = query.all()

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
                for linea in lineas_orm
            ]
            return domain_entities
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError("Error al obtener registros filtrados.") from e


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
            raise RepositoryError("Error al obtener todas las líneas salida.") from e


    def update(self, linea_id: int, linea_salida_data: LineasSalidaUpdate, linea_num: int) -> Optional[LineasSalida]:
        orm_model = self.db.query(self._get_orm_model(linea_num)).get(linea_id)
        if not orm_model:
            raise NotFoundError(f"Producción de linea entrada con id={linea_id} no encontrado.")

        update_data = linea_salida_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(orm_model, key, value)

        try:
            self.db.commit()
            self.db.refresh(orm_model)
            return LineasSalida(
                id=orm_model.id,
                fecha_p=orm_model.fecha_p,
                fecha=orm_model.fecha,
                peso_kg=orm_model.peso_kg,
                codigo_bastidor=orm_model.codigo_bastidor,
                p_lote=orm_model.p_lote,
                codigo_parrilla=orm_model.codigo_parrilla,
                codigo_obrero=orm_model.codigo_obrero,
                guid=orm_model.guid
            )
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError("Error al actualizar la producción de la linea salida.") from e

    def remove(self, linea_id: int, linea_num: int) -> bool:
        try:
            linea_orm = self.db.query(self._get_orm_model(linea_num)).get(linea_id)
            if not linea_orm:
                raise NotFoundError(f"Producción de linea salida con id={linea_id} no encontrado.")
            self.db.delete(linea_orm)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logging.error(f"FALLO DE DB DETALLADO: {e}")
            raise RepositoryError("Error al elimar linea salida.") from e


    def agregar_tara(self, linea_id: int, linea_num: int, peso_kg: float) -> Optional[LineasSalida]:
        orm_model = self._get_orm_model(linea_num)
        try:
            linea_orm = self.db.query(orm_model).filter(orm_model.id == linea_id).one_or_none()
            if linea_orm is None:
                return None

            linea_orm.peso_kg = peso_kg
            self.db.commit()
            self.db.refresh(linea_orm)

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
            self.db.rollback()
            raise RepositoryError("Error al agregar la tara a la línea salida.") from e


    def update_codigo_parrilla(self, linea_id: int, linea_num: int, valor_parrilla: str) -> Optional[LineasSalida]:
        try:
            linea_orm = self.db.query(self._get_orm_model(linea_num)).get(linea_id)
            if linea_orm is None:
                raise NotFoundError(f"Producción de linea salida con id={linea_id} no encontrado.")

            linea_orm.codigo_parrilla = valor_parrilla
            self.db.commit()
            self.db.refresh(linea_orm)

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
            self.db.rollback()
            raise RepositoryError("Error al actualizar el código de parrilla de la línea salida.") from e

    def agregar_panzas(self, items: list[dict]) -> list[LineasSalida]:
        try:
            linea_num = items[0]["linea_num"]
            orm_model = self._get_orm_model(linea_num)

            ids = [item["linea_id"] for item in items]
            nuevos_pesos = {item["linea_id"]: item["nuevo_peso"] for item in items}

            registros = (
                self.db.query(orm_model)
                .filter(orm_model.id.in_(ids))
                .all()
            )

            if len(registros) != len(ids):
                raise NotFoundError("Uno o más registros no existen.")

            for r in registros:
                r.peso_kg = nuevos_pesos[r.id]

            self.db.commit()

            return [
                LineasSalida(
                    id=r.id,
                    fecha_p=r.fecha_p,
                    fecha=r.fecha,
                    peso_kg=r.peso_kg,
                    codigo_bastidor=r.codigo_bastidor,
                    p_lote=r.p_lote,
                    codigo_parrilla=r.codigo_parrilla,
                    codigo_obrero=r.codigo_obrero,
                    guid=r.guid,
                )
                for r in registros
            ]

        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError("Error al actualizar pesos.") from e

    def update_lote(self, items: list[dict], lote:str) -> list[LineasSalida]:
        try:
            linea_num = items[0]["linea_num"]
            orm_model = self._get_orm_model(linea_num)

            ids = [item["linea_id"] for item in items]
            nuevos_pesos = {item["linea_id"]: item["nuevo_peso"] for item in items}

            registros = (
                self.db.query(orm_model)
                .filter(orm_model.id.in_(ids))
                .all()
            )

            if len(registros) != len(ids):
                raise NotFoundError("Uno o más registros no existen.")

            for r in registros:
                r.peso_kg = nuevos_pesos[r.id]

            self.db.commit()

            return [
                LineasSalida(
                    id=r.id,
                    fecha_p=r.fecha_p,
                    fecha=r.fecha,
                    peso_kg=r.peso_kg,
                    codigo_bastidor=r.codigo_bastidor,
                    p_lote=r.p_lote,
                    codigo_parrilla=r.codigo_parrilla,
                    codigo_obrero=r.codigo_obrero,
                    guid=r.guid,
                )
                for r in registros
            ]

        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError("Error al actualizar pesos.") from e

    def update_lote_by_ids(self, linea_num: int, ids: list[int], lote: str) -> list[LineasSalida]:
        orm_model = self._get_orm_model(linea_num)

        try:
            registros = (
                self.db.query(orm_model)
                .filter(orm_model.id.in_(ids))
                .all()
            )

            if not registros:
                raise NotFoundError("No se encontraron registros para actualizar el lote.")

            if len(registros) != len(ids):
                raise NotFoundError("Uno o más registros no existen.")

            for r in registros:
                r.p_lote = lote

            self.db.commit()

            return [
                LineasSalida(
                    id=r.id,
                    fecha_p=r.fecha_p,
                    fecha=r.fecha,
                    peso_kg=r.peso_kg,
                    codigo_bastidor=r.codigo_bastidor,
                    p_lote=r.p_lote,
                    codigo_parrilla=r.codigo_parrilla,
                    codigo_obrero=r.codigo_obrero,
                    guid=r.guid,
                )
                for r in registros
            ]

        except Exception as e:
            self.db.rollback()
            raise RepositoryError("Error al actualizar el lote.") from e