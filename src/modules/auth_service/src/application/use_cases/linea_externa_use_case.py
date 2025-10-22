from typing import List
from src.modules.auth_service.src.application.ports.linea_externa import ILineaExternaRepository
from src.modules.auth_service.src.domain.entities import LineaExterna

class LineaExternaUseCase:
    def __init__(self, linea_externa_repository: ILineaExternaRepository):
        self.linea_externa_repository = linea_externa_repository

    def get_all_active_lines(self) -> List[LineaExterna]:
        """Obtiene todas las líneas externas activas."""
        return self.linea_externa_repository.get_all_active()