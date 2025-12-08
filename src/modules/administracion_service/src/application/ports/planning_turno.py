from abc import ABC, abstractmethod
from typing import Tuple, List, Optional

from src.modules.administracion_service.src.domain.entities import PlanningTurno
from src.modules.administracion_service.src.infrastructure.api.schemas.planning_turno import PlanningTurnoUpdate, \
    PlanningTurnoPagination


class IPlanningTurnoRepository(ABC):

    @abstractmethod
    def get_paginated_by_filters(self, paginated_filters: PlanningTurnoPagination) -> Tuple[List[PlanningTurno], int]:
        pass

    @abstractmethod
    def exists_by_id(self, id: int) -> bool:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[PlanningTurno]:
        pass

    @abstractmethod
    def update(self, data: PlanningTurnoUpdate, id: int) -> Optional[PlanningTurno]:
        pass

    @abstractmethod
    def remove(self, id: int) -> bool:
        pass