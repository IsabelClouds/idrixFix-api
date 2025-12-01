from abc import ABC, abstractmethod
from typing import Tuple, List, Optional

from src.modules.lineas_entrada_salida_service.domain.entities import LineasSalida
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.lineas_shared import LineasFilters
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.lineas_salida import LineasSalidaUpdate


class ILineasSalidaRepository(ABC):
    @abstractmethod
    def get_paginated_by_filters(self, filters: LineasFilters, page: int, page_size: int, linea_num: int) -> Tuple[
        List[LineasSalida], int]:
        pass

    @abstractmethod
    def get_by_id(self, linea_id: int, linea_num: int) -> Optional[LineasSalida]:
        pass

    @abstractmethod
    def get_all_by_filters(self, filters: LineasFilters, linea_num: int) -> List[LineasSalida]:
        pass

    @abstractmethod
    def update(self, linea_id: int, linea_salida_data: LineasSalidaUpdate, linea_num: int) -> Optional[LineasSalida]:
        pass

    @abstractmethod
    def remove(self, linea_id: int, linea_num: int) -> bool:
        pass

    @abstractmethod
    def agregar_tara(self, linea_id: int, linea_num: int, peso_kg: float) -> Optional[LineasSalida]:
        pass

    @abstractmethod
    def update_codigo_parrilla(self, linea_id: int, linea_num: int, valor_parrilla: str) -> Optional[LineasSalida]:
        pass

    @abstractmethod
    def agregar_panza(self, linea_id: int, linea_num: int, nuevo_peso: float) -> Optional[LineasSalida]:
        pass

    @abstractmethod
    def count_by_filters(self, filters: LineasFilters, linea_num: int) -> int:
        pass
