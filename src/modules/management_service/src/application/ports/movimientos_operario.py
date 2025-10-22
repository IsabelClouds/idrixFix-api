from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from datetime import date, datetime

# Asumo que importas estas clases
from src.modules.management_service.src.domain.entities import WorkerMovement, RefMotivo, RefDestinoMotivo
from src.modules.management_service.src.infrastructure.api.schemas.movimientos_operario import (
    WorkerMovementCreate,
    WorkerMovementUpdate,
    WorkerMovementFilters,
    RefMotivoFilters, 
    RefDestinoMotivoFilters,
)

class IWorkerMovementRepository(ABC):
    """Puerto para la gestión de movimientos de operarios."""
    
    @abstractmethod
    def get_by_id(self, movement_id: int) -> Optional[WorkerMovement]:
        pass

    @abstractmethod
    def get_all_by_date(self, start_date: date, end_date: date) -> List[WorkerMovement]:
        pass
    
    @abstractmethod
    def create(self, movement_data: WorkerMovementCreate) -> WorkerMovement:
        pass
        
    @abstractmethod
    def update(
        self, movement_id: int, movement_data: WorkerMovementUpdate
    ) -> Optional[WorkerMovement]:
        pass
    
    @abstractmethod
    def delete(self, movement_id: int) -> bool:
        pass
    @abstractmethod
    def count_by_filters(
        self, filters: WorkerMovementFilters, allowed_lines: List[str] 
    ) -> int:
        """Cuenta el total de registros WorkerMovement según los filtros."""
        pass
    
    @abstractmethod
    def get_paginated_by_filters(
        self, filters: WorkerMovementFilters, page: int, page_size: int, allowed_lines: List[str] 
    ) -> Tuple[List[WorkerMovement], int]:
        """Obtiene una página de registros WorkerMovement y el conteo total."""
        pass

class IRefMotivoRepository(ABC):
    """Puerto para la gestión de motivos de referencia."""
    
    @abstractmethod
    def get_paginated_active(self, page: int, page_size: int) -> Tuple[List[RefMotivo], int]:
        """Obtiene motivos activos (estado='ACTIVO') paginados."""
        pass


class IRefDestinoMotivoRepository(ABC):
    """Puerto para la gestión de destinos de motivos de referencia."""
    
    @abstractmethod
    def get_paginated_by_motivo(
        self, id_motivo: int, page: int, page_size: int
    ) -> Tuple[List[RefDestinoMotivo], int]:
        """Obtiene destinos paginados filtrados por id_motivo."""
        pass
