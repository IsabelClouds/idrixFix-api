from math import ceil
from typing import Optional

from src.modules.administracion_service.src.application.ports.planning_turno import IPlanningTurnoRepository
from src.modules.administracion_service.src.domain.entities import PlanningTurno
from src.modules.administracion_service.src.infrastructure.api.schemas.planning_turno import (
    PlanningTurnoPagination, PlanningTurnoUpdate
)
from src.shared.exceptions import NotFoundError


class PlanningTurnoUseCase:
    def __init__(self, planning_turno_repository: IPlanningTurnoRepository):
        self.planning_turno_repository = planning_turno_repository

    def get_paginated_by_filters(self, paginated_filters: PlanningTurnoPagination):
        data, total_records = self.planning_turno_repository.get_paginated_by_filters(paginated_filters)

        total_pages = ceil(total_records / paginated_filters.page_size) if total_records > 0 else 0

        return {
            "total_records": total_records,
            "total_pages": total_pages,
            "page": paginated_filters.page,
            "page_size": paginated_filters.page_size,
            "data": data
        }

    def get_by_id(self, id: int) -> Optional[PlanningTurno]:
        planning_turno = self.planning_turno_repository.get_by_id(id)
        if not planning_turno:
            raise NotFoundError("El registro no existe")
        return planning_turno

    def update(self, id: int, data: PlanningTurnoUpdate):
        if not self.planning_turno_repository.exists_by_id(id):
            raise NotFoundError("No existe el registro")
        return self.planning_turno_repository.update(data, id)

    def remove(self, id: int) -> bool:
        if not self.planning_turno_repository.exists_by_id(id):
            raise NotFoundError("No existe el registro")
        return self.planning_turno_repository.remove(id)
