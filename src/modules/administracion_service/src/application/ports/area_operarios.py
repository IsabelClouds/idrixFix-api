from abc import ABC, abstractmethod
from typing import Optional

from src.modules.administracion_service.src.domain.entities import AreaOperarios
from src.modules.administracion_service.src.infrastructure.api.schemas.area_operarios import AreaOperariosRequest


class IAreaOperarioRepository(ABC):

    @abstractmethod
    def create(self, data: AreaOperariosRequest) -> AreaOperarios:
        pass

    @abstractmethod
    def get_all(self) -> list[AreaOperarios]:
        pass

    @abstractmethod
    def exists_by_name(self, nombre: str) -> bool:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[AreaOperarios]:
        pass
    #
    # def delete(self, id: int) -> bool:
    #     pass

    @abstractmethod
    def update(self, data: AreaOperariosRequest, id: int) -> Optional[AreaOperarios]:
        pass