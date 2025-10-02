from abc import ABC, abstractmethod
from typing import List, Optional
from src.modules.auth_service.src.infrastructure.api.schemas.sesiones import (
    SesionCreate,
)
from src.modules.auth_service.src.infrastructure.db.models import SesionUsuario


class ISesionRepository(ABC):

    @abstractmethod
    def get_all(self) -> List[SesionUsuario]:
        pass

    @abstractmethod
    def get_by_id(self, sesion_id: int) -> Optional[SesionUsuario]:
        pass

    @abstractmethod
    def get_by_token(self, token: str) -> Optional[SesionUsuario]:
        pass

    @abstractmethod
    def get_by_usuario_id(self, usuario_id: int) -> List[SesionUsuario]:
        pass

    @abstractmethod
    def get_active_by_usuario_id(self, usuario_id: int) -> List[SesionUsuario]:
        pass

    @abstractmethod
    def create(self, sesion_data: SesionCreate) -> SesionUsuario:
        pass

    @abstractmethod
    def soft_delete(self, sesion_id: int) -> Optional[SesionUsuario]:
        pass

    @abstractmethod
    def invalidate_by_token(self, token: str) -> Optional[SesionUsuario]:
        pass

    @abstractmethod
    def invalidate_all_by_usuario_id(self, usuario_id: int) -> bool:
        pass

    @abstractmethod
    def cleanup_expired_sessions(self) -> int:
        pass
