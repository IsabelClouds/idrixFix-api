from abc import ABC, abstractmethod
from typing import Optional

from src.modules.lineas_entrada_salida_service.src.domain.entities import ControlMiga


class IControlMigaRepository(ABC):
    @abstractmethod
    def create(self, linea_num: int, registro: int, p_miga: float, porcentaje: float) -> ControlMiga:
        pass

    @abstractmethod
    def get_by_registro(self, linea_num: int, registro: int) -> Optional[ControlMiga]:
        pass

    @abstractmethod
    def update(self, id: int, p_miga: float, porcentaje: float) -> Optional[ControlMiga]:
        pass