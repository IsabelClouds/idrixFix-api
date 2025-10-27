from src.modules.auth_service.src.infrastructure.api.schemas.auditoria import AuditoriaLogFilters
from src.modules.auth_service.src.infrastructure.db.models import AuditoriaLogORM
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple

class IAuditoriaLogRepository(ABC):
    
    @abstractmethod
    def create_log(self, log_data: Dict[str, Any]) -> bool:
        """Crea un nuevo registro de log de auditoría."""
        pass
    @abstractmethod
    def count_by_filters(self, filters: AuditoriaLogFilters) -> int:
        """Cuenta logs según los filtros proporcionados."""
        pass
        
    @abstractmethod
    def get_paginated_by_filters(
        self, filters: AuditoriaLogFilters, page: int, page_size: int
    ) -> Tuple[List[AuditoriaLogORM], int]:
        """Obtiene logs paginados según filtros y devuelve ORMs y conteo."""
        pass