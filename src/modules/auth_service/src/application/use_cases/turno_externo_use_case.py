from typing import List
from src.modules.auth_service.src.application.ports.turno_externo_repository import ITurnoExternaRepository
from src.modules.auth_service.src.domain.entities import TurnoExterno

class TurnoExternaUseCase:
    
    def __init__(self, turno_externa_repository: ITurnoExternaRepository):
        self.turno_externa_repository = turno_externa_repository

    def get_all_active_turnos(self) -> List[TurnoExterno]:
        """Obtiene todas los turnos externos activos."""
        return self.turno_externa_repository.get_all_active()