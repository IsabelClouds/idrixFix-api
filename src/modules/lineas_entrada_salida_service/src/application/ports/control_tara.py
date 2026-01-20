from abc import ABC, abstractmethod
from typing import Optional

from src.modules.lineas_entrada_salida_service.src.infrastructure.api.schemas.control_tara import TaraCreate
from src.modules.lineas_entrada_salida_service.src.domain.entities import ControlTara


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
    def exists_by_nombre_and_peso_kg(self, nombre: str, peso_kg_tara: float) -> bool:
        pass

    @abstractmethod
    def get_principal(self) -> Optional[ControlTara]:
        pass

    @abstractmethod
    def set_principal(self, tara_id, principal: bool):
        pass
