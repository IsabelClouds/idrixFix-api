from typing import Optional, List, Dict, Any

from src.modules.auth_service.src.application.use_cases.audit_use_case import AuditUseCase
from src.modules.lineas_entrada_salida_service.application.ports.control_tara import IControlTaraRepository
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.control_tara import TaraCreate, TaraResponse
from src.modules.lineas_entrada_salida_service.domain.entities import ControlTara
from src.shared.exceptions import AlreadyExistsError, ValidationError


class ControlTaraUseCase:
    def __init__(self, control_tara_repository: IControlTaraRepository, audit_use_case: AuditUseCase):
        self.control_tara_repository = control_tara_repository
        self.audit_use_case = audit_use_case

    def create_tara(self, tara_data: TaraCreate, user_data: Dict[str, Any]) -> ControlTara:
        exist = self.control_tara_repository.exists_by_peso_kg(tara_data.peso_kg)
        if exist:
            raise AlreadyExistsError("Ya existe una tara con este peso asignado")
        if tara_data.peso_kg <= 0:
            raise ValidationError("El peso de la tara debe ser mayor a cero")
        nueva_tara = self.control_tara_repository.create(tara_data)
        self.audit_use_case.log_action(
            accion="CREATE",
            user_id=user_data.get("user_id"),
            modelo="control_tara",
            entidad_id=nueva_tara.id,
            datos_nuevos=TaraResponse.model_validate(nueva_tara).model_dump(mode="json")
        )
        return nueva_tara

    def get_all_taras(self) -> List[ControlTara]:
        return self.control_tara_repository.get_all()

    def get_tara_by_id(self, tara_id: int) -> Optional[ControlTara]:
        return self.control_tara_repository.get_by_id(tara_id)

    def soft_delete(self, tara_id: int, user_data: Dict[str, Any]) -> bool:
        tara_data = self.control_tara_repository.get_by_id(tara_id)
        datos_anteriores =  TaraResponse.model_validate(tara_data).model_dump(mode="json")
        self.audit_use_case.log_action(
            accion="DELETE",
            user_id=user_data.get("user_id"),
            modelo="control_tara",
            entidad_id=tara_id,
            datos_anteriores=datos_anteriores
        )
        return  self.control_tara_repository.soft_delete(tara_id)