import logging
from typing import Tuple, List, Optional

from sqlalchemy import func, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.modules.administracion_service.src.application.ports.control_lote_asiglinea import \
    IControlLoteAsiglineaRepository
from src.modules.administracion_service.src.domain.entities import ControlLoteAsiglinea
from src.modules.administracion_service.src.infrastructure.api.schemas.control_lote_asiglinea import \
    ControlLoteAsiglineaFilters, ControlLoteAsiglineaPagination, ControlLoteAsiglineaUpdate
from src.modules.administracion_service.src.infrastructure.db.models import ControlLoteAsiglineaORM
from src.shared.exceptions import RepositoryError, NotFoundError


class ControlLoteAsiglineaRepository(IControlLoteAsiglineaRepository):
    def __init__(self, db: Session):
        self.db = db

    def _apply_filters(self, query, filters: ControlLoteAsiglineaFilters):
        conditions = []

        if filters:
            if filters.fecha_p is not None:
                conditions.append(ControlLoteAsiglineaORM.fecha_p == filters.fecha_p)

            if filters.lote:
                conditions.append(ControlLoteAsiglineaORM.lote == filters.lote)

            if filters.linea:
                conditions.append(ControlLoteAsiglineaORM.linea == filters.linea)

        if conditions:
            query = query.filter(and_(*conditions))

        return query

    def _count_by_filters(self, filters: ControlLoteAsiglineaFilters) -> int:
        try:
            query = self.db.query(func.count(ControlLoteAsiglineaORM.id))

            query = self._apply_filters(query, filters)

            return query.scalar() or 0
        except SQLAlchemyError as e:
            raise RepositoryError(f"Error al contar .") from e

    def exists_by_id(self, id: int) -> bool:
        try:
            lote_orm = (
                self.db.query(ControlLoteAsiglineaORM.id)
                .filter(ControlLoteAsiglineaORM.id == id)
                .first()
            )
            return lote_orm is not None

        except SQLAlchemyError as e:
            raise RepositoryError("Error al consultar el lote.") from e

    def get_by_id(self, id: int) -> Optional[ControlLoteAsiglinea]:
        try:
            linea_orm = (
                self.db.query(ControlLoteAsiglineaORM)
                .filter(ControlLoteAsiglineaORM.id == id)
                .first()
            )
            if not linea_orm:
                return None
            return ControlLoteAsiglinea(
                id=linea_orm.id,
                fecha_p=linea_orm.fecha_p,
                lote=linea_orm.lote,
                linea=linea_orm.linea,
                estado=linea_orm.estado,
                fecha_asig=linea_orm.fecha_asig,
                tipo_limpieza=linea_orm.tipo_limpieza,
                turno=linea_orm.turno
            )

        except SQLAlchemyError as e:
            raise RepositoryError("Error al consultar el lote.") from e

    def get_paginated_by_filters(self, paginated_filters: ControlLoteAsiglineaPagination) -> Tuple[
        List[ControlLoteAsiglinea], int]:
        filters = ControlLoteAsiglineaFilters(
            fecha_p=paginated_filters.fecha_p,
            lote=paginated_filters.lote,
            linea=paginated_filters.linea
        )
        try:
            total_records = self._count_by_filters(filters)

            if total_records == 0:
                return [], 0

            base_query = self.db.query(ControlLoteAsiglineaORM)
            data_query = self._apply_filters(base_query, filters)

            data_query = data_query.order_by(ControlLoteAsiglineaORM.fecha_p.desc(),
                                             ControlLoteAsiglineaORM.fecha_asig.desc())

            offset = (paginated_filters.page - 1) * paginated_filters.page_size
            data_query = data_query.limit(paginated_filters.page_size).offset(offset)

            lote_asiglineas = data_query.all()

            domain_entities = [
                ControlLoteAsiglinea(
                    id=l.id,
                    fecha_p=l.fecha_p,
                    lote=l.lote,
                    linea=l.linea,
                    estado=l.estado,
                    fecha_asig=l.fecha_asig,
                    tipo_limpieza=l.tipo_limpieza,
                    turno=l.turno
                )
                for l in lote_asiglineas
            ]

            return domain_entities, total_records
        except SQLAlchemyError as e:
            logging.error(e)
            raise RepositoryError("Error al obtener todos los lotes.") from e

    def update(self, data: ControlLoteAsiglineaUpdate, id: int) -> Optional[ControlLoteAsiglinea]:
        lote_orm = self.db.query(ControlLoteAsiglineaORM).get(id)

        if lote_orm is None:
            raise NotFoundError("Lote no encontrado.")

        updated_data = data.model_dump(exclude_unset=True)
        for k, v in updated_data.items():
            setattr(lote_orm, k, v)

        try:
            self.db.commit()
            self.db.refresh(lote_orm)
            return ControlLoteAsiglinea(
                id=lote_orm.id,
                fecha_p=lote_orm.fecha_p,
                lote=lote_orm.lote,
                linea=lote_orm.linea,
                estado=lote_orm.estado,
                fecha_asig=lote_orm.fecha_asig,
                tipo_limpieza=lote_orm.tipo_limpieza,
                turno=lote_orm.turno
            )
        except SQLAlchemyError as e:
            self.db.rollback()

    def remove(self, id: int) -> bool:
        try:
            linea_orm = (
                self.db.query(ControlLoteAsiglineaORM)
                .filter(ControlLoteAsiglineaORM.id == id)
                .first()
            )

            if linea_orm is None:
                raise NotFoundError("Lote no encontrado.")

            self.db.delete(linea_orm)
            self.db.commit()
            return True

        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError("Error al eliminar el lote.") from e
