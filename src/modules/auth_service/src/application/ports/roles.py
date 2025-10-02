from abc import ABC, abstractmethod
from typing import List, Optional
from src.modules.auth_service.src.infrastructure.api.schemas.roles import (
    RolCreate,
    RolUpdate,
)
from src.modules.auth_service.src.infrastructure.db.models import Rol


class IRolRepository(ABC):

    @abstractmethod
    def get_all(self) -> List[Rol]:
        pass

    @abstractmethod
    def get_by_id(self, rol_id: int) -> Optional[Rol]:
        pass

    @abstractmethod
    def get_by_nombre(self, nombre: str) -> Optional[Rol]:
        pass

    @abstractmethod
    def create(self, rol_data: RolCreate) -> Rol:
        pass

    @abstractmethod
    def update(
        self, rol_id: int, rol_data: RolUpdate
    ) -> Optional[Rol]:
        pass

    @abstractmethod
    def soft_delete(self, rol_id: int) -> Optional[Rol]:
        pass

    @abstractmethod
    def get_with_permisos(self, rol_id: int) -> Optional[Rol]:
        pass
