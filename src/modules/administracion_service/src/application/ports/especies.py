from abc import ABC, abstractmethod
from typing import Optional, Tuple, List

from src.modules.administracion_service.src.domain.entities import Especie
from src.modules.administracion_service.src.infrastructure.api.schemas.especies import EspeciesRequest, \
    EspeciesPaginated


class IEspeciesRepository(ABC):

    @abstractmethod
    def get_all_paginated(self, pagination: EspeciesPaginated) -> Tuple[List[Especie], int]:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Especie]:
        pass

    @abstractmethod
    def exists_by_id(self, id: int) -> bool:
        pass

    @abstractmethod
    def create(self, data: EspeciesRequest) -> Especie:
        pass

    @abstractmethod
    def update(self, data: EspeciesRequest, id: int) -> Optional[Especie]:
        pass

    @abstractmethod
    def exists_by_nombre(self, name: str) -> bool:
        pass
