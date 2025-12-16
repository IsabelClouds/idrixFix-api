from typing import List, Optional, Dict, Any

from src.modules.administracion_service.src.application.ports.area_operarios import IAreaOperarioRepository
from src.modules.administracion_service.src.domain.entities import AreaOperarios
from src.modules.administracion_service.src.infrastructure.api.schemas.area_operarios import AreaOperariosRequest, \
    AreaOperariosResponse
from src.modules.auth_service.src.application.use_cases.audit_use_case import AuditUseCase
from src.shared.exceptions import ValidationError, AlreadyExistsError, NotFoundError


class AreaOperariosUseCase:
    def __init__(self, area_operarios_repository: IAreaOperarioRepository, audit_use_case: AuditUseCase):
        self.area_operarios_repository = area_operarios_repository
        self.audit_use_case = audit_use_case

    def get_all_areas_operarios(self) -> List[AreaOperarios]:
        return self.area_operarios_repository.get_all()

    def get_area_by_id(self, id: int) -> Optional[AreaOperarios]:
        area = self.area_operarios_repository.get_by_id(id)
        if not area:
            raise NotFoundError("No existe el area")
        return area

    def create_area_operarios(self, data: AreaOperariosRequest, user_data: Dict[str, Any]) -> AreaOperarios:
        if not data.area_nombre:
            raise ValidationError("El nombre no puede estar vacío")

        exist = self.area_operarios_repository.exists_by_name(data.area_nombre)
        if exist:
            raise AlreadyExistsError("Ya existe un area con este nombre")

        nueva_area= self.area_operarios_repository.create(data)
        self.audit_use_case.log_action(
            accion="CREATE",
            user_id=user_data.get("user_id"),
            modelo="fm_area_operarios",
            entidad_id=nueva_area.area_id,
            datos_nuevos=AreaOperariosResponse.model_validate(nueva_area).model_dump(mode="json")
        )
        return nueva_area

    def update_area_operarios(self, data: AreaOperariosRequest, id: int, user_data: Dict[str, Any]) -> Optional[AreaOperarios]:
        area = self.area_operarios_repository.get_by_id(id)

        if not area:
            raise NotFoundError("No se encontró el area")

        exist = self.area_operarios_repository.exists_by_name(data.area_nombre)
        if exist:
            raise AlreadyExistsError("Ya existe un area con este nombre")

        updated_area = self.area_operarios_repository.update(data, id)
        self.audit_use_case.log_action(
            accion="UPDATE",
            user_id=user_data.get("user_id"),
            modelo="fm_area_operarios",
            entidad_id=area.area_id,
            datos_nuevos=AreaOperariosResponse.model_validate(updated_area).model_dump(mode="json"),
            datos_anteriores=AreaOperariosResponse.model_validate(area).model_dump(mode="json")
        )
        return updated_area

    def remove_area(self, id: int, user_data: Dict[str, Any]) -> bool:
        exists = self.area_operarios_repository.exists_by_id(id)
        if not exists:
            raise NotFoundError("No existe el area")

        area = self.area_operarios_repository.get_by_id(id)

        self.audit_use_case.log_action(
            accion="DELETE",
            user_id=user_data.get("user_id"),
            modelo="fm_area_operarios",
            entidad_id=id,
            datos_anteriores=AreaOperariosResponse.model_validate(area).model_dump(mode="json")
        )

        return self.area_operarios_repository.soft_delete(id)