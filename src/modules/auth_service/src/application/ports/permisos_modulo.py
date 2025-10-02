from abc import ABC, abstractmethod
from typing import List, Optional
from src.modules.auth_service.src.infrastructure.api.schemas.permisos_modulo import (
    PermisoModuloCreate,
    PermisoModuloUpdate,
)
from src.modules.auth_service.src.infrastructure.db.models import PermisoModulo
from src.modules.auth_service.src.domain.entities import ModuloEnum


class IPermisoModuloRepository(ABC):

    @abstractmethod
    def get_all(self) -> List[PermisoModulo]:
        pass

    @abstractmethod
    def get_by_id(self, permiso_id: int) -> Optional[PermisoModulo]:
        pass

    @abstractmethod
    def get_by_rol_id(self, rol_id: int) -> List[PermisoModulo]:
        pass

    @abstractmethod
    def get_by_rol_and_modulo(self, rol_id: int, modulo: ModuloEnum) -> Optional[PermisoModulo]:
        pass

    @abstractmethod
    def create(self, permiso_data: PermisoModuloCreate) -> PermisoModulo:
        pass

    @abstractmethod
    def update(
        self, permiso_id: int, permiso_data: PermisoModuloUpdate
    ) -> Optional[PermisoModulo]:
        pass

    @abstractmethod
    def soft_delete(self, permiso_id: int) -> Optional[PermisoModulo]:
        pass

    @abstractmethod
    def delete_by_rol_id(self, rol_id: int) -> bool:
        pass
