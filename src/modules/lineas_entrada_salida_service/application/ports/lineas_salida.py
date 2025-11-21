from abc import ABC, abstractmethod
from typing import Tuple, List, Optional

from src.modules.lineas_entrada_salida_service.domain.entities import LineasSalida
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.lineas_filters import LineasFilters
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.lineas_salida import LineasSalidaUpdate


class ILineasSalidaRepository(ABC):
    @abstractmethod
    def get_paginated_by_filters(self, filters: LineasFilters, page: int, page_size: int, linea_num: int) -> Tuple[List[LineasSalida], int]:
        pass

    @abstractmethod
    def get_by_id(self, linea_id: int, linea_num: int) -> Optional[LineasSalida]:
        pass

    # @abstractmethod
    # def update(self, linea_id: int, linea_salida_data: LineasSalidaUpdate, linea_num: int) -> Optional[LineasSalida]:
    #     pass

    @abstractmethod
    def remove(self, linea_id: int, linea_num: int) -> bool:
        pass