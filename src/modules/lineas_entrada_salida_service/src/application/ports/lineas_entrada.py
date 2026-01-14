from abc import abstractmethod, ABC
from typing import List, Tuple, Optional

from src.modules.lineas_entrada_salida_service.src.domain.entities import LineasEntrada
from src.modules.lineas_entrada_salida_service.src.infrastructure.api.schemas.lineas_entrada import LineasEntradaUpdate
from src.modules.lineas_entrada_salida_service.src.infrastructure.api.schemas.lineas_shared import \
    LineasFilters


class ILineasEntradaRepository(ABC):
    @abstractmethod
    def get_paginated_by_filters(self, filters: LineasFilters, page: int, page_size: int, linea_num: int) -> Tuple[List[LineasEntrada], int]:
        pass

    @abstractmethod
    def get_by_id(self, linea_id: int, linea_num: int) -> Optional[LineasEntrada]:
        pass

    @abstractmethod
    def update(self, linea_id: int, linea_entrada_data: LineasEntradaUpdate, linea_num: int) -> Optional[LineasEntrada]:
        pass

    @abstractmethod
    def remove(self, linea_id: int, linea_num: int) -> bool:
        pass

    @abstractmethod
    def update_codigo_parrilla(self, linea_id: int, linea_num: int, valor_parrilla: str, valor_secuencia: str) -> Optional[LineasEntrada]:
        pass

    @abstractmethod
    def agregar_panzas(self, items: list[dict]) -> list[LineasEntrada]:
        pass

    @abstractmethod
    def get_all_by_filters(self, filters: LineasFilters, linea_num: int) -> List[LineasEntrada]:
        pass