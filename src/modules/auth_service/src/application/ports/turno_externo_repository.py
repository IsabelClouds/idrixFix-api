from abc import ABC, abstractmethod
from typing import Optional, List
from src.modules.auth_service.src.domain.entities import TurnoExterno 

class ITurnoExternaRepository(ABC):
    
    @abstractmethod
    def get_by_id(self, id_turno: int) -> Optional[TurnoExterno]:
        """
        Busca un turno externo por su ID.
        Retorna una entidad de dominio 'TurnoExterno' o None.
        """
        pass

    @abstractmethod
    def exists_by_id(self, id_turno: int) -> bool:
        """
        Verifica de forma rápida si un turno existe y está activo.
        """
        pass

    @abstractmethod
    def get_all_active(self) -> List[TurnoExterno]:
        """
        Obtiene todas las líneas de trabajo externas que están activas.
        """
        pass