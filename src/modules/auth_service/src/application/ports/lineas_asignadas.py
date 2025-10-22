from abc import ABC, abstractmethod
from typing import List, Optional
from src.modules.auth_service.src.infrastructure.db.models import UsuarioLineaAsignada

class ILineaAsignadaRepository(ABC):

    @abstractmethod
    def get_by_usuario_id(self, id_usuario: int) -> List[UsuarioLineaAsignada]:
        """Obtiene todas las líneas asignadas a un usuario"""
        pass

    @abstractmethod
    def asignar(self, id_usuario: int, id_linea_externa: int) -> UsuarioLineaAsignada:
        """Asigna una línea externa a un usuario interno"""
        pass

    @abstractmethod
    def remover(self, id_usuario: int, id_linea_externa: int) -> bool:
        """Remueve la asignación de una línea a un usuario"""
        pass

    @abstractmethod
    def verificar_existencia(self, id_usuario: int, id_linea_externa: int) -> bool:
        """Verifica si una asignación ya existe"""
        pass