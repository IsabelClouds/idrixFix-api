from abc import ABC, abstractmethod
from typing import Tuple, List, Optional

from src.modules.administracion_service.src.domain.entities import ControlLoteAsiglinea
from src.modules.administracion_service.src.infrastructure.api.schemas.control_lote_asiglinea import \
    ControlLoteAsiglineaPagination, ControlLoteAsiglineaUpdate


class IControlLoteAsiglineaRepository(ABC):

    @abstractmethod
    def get_paginated_by_filters(self, paginated_filters: ControlLoteAsiglineaPagination) -> Tuple[List[ControlLoteAsiglinea], int]:
        pass

    @abstractmethod
    def exists_by_id(self, id: int) -> bool:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[ControlLoteAsiglinea]:
        pass

    @abstractmethod
    def update(self, data: ControlLoteAsiglineaUpdate, id: int) -> Optional[ControlLoteAsiglinea]:
        pass

    @abstractmethod
    def remove(self, id: int) -> bool:
        pass