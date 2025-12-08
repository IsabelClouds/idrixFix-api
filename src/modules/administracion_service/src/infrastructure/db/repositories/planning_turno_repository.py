from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, and_

from src.modules.administracion_service.src.application.ports.planning_turno import IPlanningTurnoRepository
from src.modules.administracion_service.src.domain.entities import PlanningTurno
from src.modules.administracion_service.src.infrastructure.api.schemas.planning_turno import (
    PlanningTurnoFilters, PlanningTurnoPagination, PlanningTurnoUpdate
)
from src.modules.administracion_service.src.infrastructure.db.models import PlanningTurnoORM
from src.shared.exceptions import RepositoryError, NotFoundError


class PlanningTurnoRepository(IPlanningTurnoRepository):
    def __init__(self, db: Session):
        self.db = db

    def _apply_filters(self, query, filters: PlanningTurnoFilters):
        conditions = []

        if filters.fecha_p:
            conditions.append(PlanningTurnoORM.plnn_fecha_p == filters.fecha_p)

        if filters.turno:
            conditions.append(PlanningTurnoORM.plnn_turno == filters.turno)

        if filters.linea:
            conditions.append(PlanningTurnoORM.plnn_linea == filters.linea)

        if conditions:
            query = query.filter(and_(*conditions))

        return query

    def _count_by_filters(self, filters: PlanningTurnoFilters) -> int:
        try:
            query = self.db.query(func.count(PlanningTurnoORM.plnn_id))
            query = self._apply_filters(query, filters)
            return query.scalar() or 0
        except SQLAlchemyError as e:
            raise RepositoryError("Error al contar registros.") from e

    def exists_by_id(self, id: int) -> bool:
        try:
            return (
                self.db.query(PlanningTurnoORM.plnn_id)
                .filter(PlanningTurnoORM.plnn_id == id)
                .first()
            ) is not None
        except SQLAlchemyError as e:
            raise RepositoryError("Error al validar existencia.") from e

    def get_by_id(self, id: int) -> Optional[PlanningTurno]:
        try:
            orm = (
                self.db.query(PlanningTurnoORM)
                .filter(PlanningTurnoORM.plnn_id == id)
                .first()
            )
            if not orm:
                return None

            return PlanningTurno(
                plnn_id=orm.plnn_id,
                plnn_fecha_p=orm.plnn_fecha_p,
                plnn_turno=orm.plnn_turno,
                plnn_linea=orm.plnn_linea,
                plnn_hora_fin=orm.plnn_hora_fin
            )
        except SQLAlchemyError as e:
            raise RepositoryError("Error al obtener registro.") from e

    def get_paginated_by_filters(self, paginated_filters: PlanningTurnoPagination) -> Tuple[List[PlanningTurno], int]:
        filters = PlanningTurnoFilters(
            fecha_p=paginated_filters.fecha_p,
            turno=paginated_filters.turno,
            linea=paginated_filters.linea,
        )

        try:
            total_records = self._count_by_filters(filters)
            if total_records == 0:
                return [], 0

            query = self.db.query(PlanningTurnoORM)
            query = self._apply_filters(query, filters)

            query = query.order_by(
                PlanningTurnoORM.plnn_fecha_p.desc(),
                PlanningTurnoORM.plnn_turno.asc()
            )

            offset = (paginated_filters.page - 1) * paginated_filters.page_size

            rows = query.limit(paginated_filters.page_size).offset(offset).all()

            entities = [
                PlanningTurno(
                    plnn_id=r.plnn_id,
                    plnn_fecha_p=r.plnn_fecha_p,
                    plnn_turno=r.plnn_turno,
                    plnn_linea=r.plnn_linea,
                    plnn_hora_fin=r.plnn_hora_fin
                )
                for r in rows
            ]

            return entities, total_records

        except SQLAlchemyError as e:
            raise RepositoryError("Error en paginación.") from e

    def update(self, data: PlanningTurnoUpdate, id: int) -> Optional[PlanningTurno]:
        orm = self.db.query(PlanningTurnoORM).get(id)

        if not orm:
            raise NotFoundError("Registro no encontrado.")

        new_data = data.model_dump(exclude_unset=True)
        for k, v in new_data.items():
            setattr(orm, k, v)

        try:
            self.db.commit()
            self.db.refresh(orm)

            return PlanningTurno(
                plnn_id=orm.plnn_id,
                plnn_fecha_p=orm.plnn_fecha_p,
                plnn_turno=orm.plnn_turno,
                plnn_linea=orm.plnn_linea,
                plnn_hora_fin=orm.plnn_hora_fin
            )
        except SQLAlchemyError:
            self.db.rollback()
            raise RepositoryError("Error al actualizar registro.")

    def remove(self, id: int) -> bool:
        orm = (
            self.db.query(PlanningTurnoORM)
            .filter(PlanningTurnoORM.plnn_id == id)
            .first()
        )

        if not orm:
            raise NotFoundError("Registro no encontrado.")

        try:
            self.db.delete(orm)
            self.db.commit()
            return True
        except SQLAlchemyError:
            self.db.rollback()
            raise RepositoryError("Error al eliminar registro.")

