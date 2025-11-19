from typing import Optional

from src.modules.lineas_entrada_salida_service.application.ports.control_tara import IControlTaraRepository
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.control_tara import TaraCreate
from src.modules.lineas_entrada_salida_service.domain.entities import ControlTara


class ControlTaraUseCase:
    def __init__(self, control_tara_repository: IControlTaraRepository):
        self.control_tara_repository = control_tara_repository

    def create_tara(self, tara_data: TaraCreate) -> ControlTara:
        return self.control_tara_repository.create(tara_data)

    def get_tara_by_id(self, tara_id: int) -> Optional[ControlTara]:
        self.control_tara_repository.get_by_id(tara_id)