from abc import ABC, abstractmethod
from typing import List, Optional
from src.modules.auth_service.src.infrastructure.api.schemas.usuarios import (
    UsuarioCreate,
    UsuarioUpdate,
)
from src.modules.auth_service.src.infrastructure.db.models import Usuario


class IUsuarioRepository(ABC):

    @abstractmethod
    def get_all(self) -> List[Usuario]:
        pass

    @abstractmethod
    def get_by_id(self, usuario_id: int) -> Optional[Usuario]:
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[Usuario]:
        pass

    @abstractmethod
    def create(self, usuario_data: UsuarioCreate) -> Usuario:
        pass

    @abstractmethod
    def update(
        self, usuario_id: int, usuario_data: UsuarioUpdate
    ) -> Optional[Usuario]:
        pass

    @abstractmethod
    def soft_delete(self, usuario_id: int) -> Optional[Usuario]:
        pass

    @abstractmethod
    def authenticate(self, username: str, password: str) -> Optional[Usuario]:
        pass

    @abstractmethod
    def update_last_login(self, usuario_id: int) -> Optional[Usuario]:
        pass
