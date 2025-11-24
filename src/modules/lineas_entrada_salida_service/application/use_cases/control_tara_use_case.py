from typing import Optional, List

from src.modules.lineas_entrada_salida_service.application.ports.control_tara import IControlTaraRepository
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.control_tara import TaraCreate
from src.modules.lineas_entrada_salida_service.domain.entities import ControlTara
from src.shared.exceptions import AlreadyExistsError


class ControlTaraUseCase:
    def __init__(self, control_tara_repository: IControlTaraRepository):
        self.control_tara_repository = control_tara_repository

    def create_tara(self, tara_data: TaraCreate) -> ControlTara:
        exist = self.control_tara_repository.exists_by_peso_kg(tara_data.peso_kg)
        if exist:
            raise AlreadyExistsError("Ya existe una tara con este peso asignado")
        return self.control_tara_repository.create(tara_data)

    def get_all_taras(self) -> List[ControlTara]:
        return self.control_tara_repository.get_all()

    def get_tara_by_id(self, tara_id: int) -> Optional[ControlTara]:
        return self.control_tara_repository.get_by_id(tara_id)

    #TODO Auditoria
    def soft_delete(self, tara_id: int) -> bool:
        return  self.control_tara_repository.soft_delete(tara_id)