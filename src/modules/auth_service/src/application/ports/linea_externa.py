from abc import ABC, abstractmethod
from typing import Optional, List
# Importa la nueva entidad de dominio que acabamos de crear
from src.modules.auth_service.src.domain.entities import LineaExterna 

class ILineaExternaRepository(ABC):
    
    @abstractmethod
    def get_by_id(self, id_linea: int) -> Optional[LineaExterna]:
        """
        Busca una línea externa por su ID.
        Retorna una entidad de dominio 'LineaExterna' o None.
        """
        pass

    @abstractmethod
    def exists_by_id(self, id_linea: int) -> bool:
        """
        Verifica de forma rápida si una línea existe y está activa.
        """
        pass
    @abstractmethod
    def get_all_active(self) -> List[LineaExterna]:
        """
        Obtiene todas las líneas de trabajo externas que están activas.
        """
        pass