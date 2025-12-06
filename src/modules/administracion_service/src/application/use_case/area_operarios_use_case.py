from typing import List, Optional

from src.modules.administracion_service.src.application.ports.area_operarios import IAreaOperarioRepository
from src.modules.administracion_service.src.domain.entities import AreaOperarios
from src.modules.administracion_service.src.infrastructure.api.schemas.area_operarios import AreaOperariosRequest
from src.shared.exceptions import ValidationError, AlreadyExistsError, NotFoundError


class AreaOperariosUseCase:
    def __init__(self, area_operarios_repository: IAreaOperarioRepository):
        self.area_operarios_repository = area_operarios_repository

    def get_all_areas_operarios(self) -> List[AreaOperarios]:
        return self.area_operarios_repository.get_all()

    def get_area_by_id(self, id: int) -> Optional[AreaOperarios]:
        area = self.area_operarios_repository.get_by_id(id)
        if not area:
            raise NotFoundError("No existe el area")
        return area

    def create_area_operarios(self, data: AreaOperariosRequest) -> AreaOperarios:
        if not data.area_nombre:
            raise ValidationError("El nombre no puede estar vacío")

        exist = self.area_operarios_repository.exists_by_name(data.area_nombre)
        if exist:
            raise AlreadyExistsError("Ya existe un area con este nombre")

        return self.area_operarios_repository.create(data)

    def update_area_operarios(self, data: AreaOperariosRequest, id: int) -> Optional[AreaOperarios]:
        area = self.area_operarios_repository.get_by_id(id)

        if not area:
            raise NotFoundError("No se encontró el area")

        return self.area_operarios_repository.update(data, id)

    def remove_area(self, id: int) -> bool:
        exists = self.area_operarios_repository.exists_by_id(id)
        if not exists:
            raise NotFoundError("No existe el area")

        return self.area_operarios_repository.soft_delete(id)