from abc import ABC, abstractmethod
from typing import Optional

from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.control_tara import TaraCreate
from src.modules.lineas_entrada_salida_service.domain.entities import ControlTara


class IControlTaraRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[ControlTara]:
        pass

    @abstractmethod
    def create(self, tara_data: TaraCreate) -> ControlTara:
        pass

    @abstractmethod
    def get_by_id(self, tara_id: int) -> Optional[ControlTara]:
        pass

    @abstractmethod
    def soft_delete(self, tara_id: int) -> bool:
        pass

    @abstractmethod
    def exists_by_peso_kg(self, peso_kg_tara: float) -> bool:
        pass
