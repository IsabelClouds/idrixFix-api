from abc import ABC, abstractmethod
from typing import List
from src.modules.auth_service.src.infrastructure.db.models import UsuarioTurnoAsignado

class ITurnoAsignadoRepository(ABC):

    @abstractmethod
    def get_by_usuario_id(self, id_usuario: int) -> List[UsuarioTurnoAsignado]:
        """Obtiene todos los turnos asignados a un usuario"""
        pass

    @abstractmethod
    def asignar(self, id_usuario: int, id_turno_externo: int) -> UsuarioTurnoAsignado:
        """Asigna un turno externo a un usuario interno"""
        pass

    @abstractmethod
    def remover(self, id_usuario: int, id_turno_externo: int) -> bool:
        """Remueve la asignación de un turno a un usuario"""
        pass

    @abstractmethod
    def verificar_existencia(self, id_usuario: int, id_turno_externo: int) -> bool:
        """Verifica si una asignación ya existe"""
        pass