from typing import List, Optional, Dict, Any # <-- Añadido Dict y Any
from datetime import date, datetime
from math import ceil

# Importar el puerto y los schemas
from src.modules.management_service.src.application.ports.movimientos_operario import (
    IWorkerMovementRepository, IRefMotivoRepository, IRefDestinoMotivoRepository
)
from src.modules.management_service.src.infrastructure.api.schemas.movimientos_operario import (
    WorkerMovementCreate,
    WorkerMovementUpdate,
    WorkerMovementPagination,
    WorkerMovementFilters,
    WorkerMovementPaginatedResponse,
    WorkerMovementResponse, # Aunque Use Case retorna la entidad, la importo por contexto
    RefMotivoPagination, 
    RefDestinoMotivoPagination, 
    RefMotivoFilters, 
    RefDestinoMotivoFilters

)
from src.modules.management_service.src.domain.entities import WorkerMovement, RefMotivo, RefDestinoMotivo


class WorkerMovementUseCases:
    def __init__(self, repository: IWorkerMovementRepository):
        self.repository = repository

    def get_movement_by_id(self, movement_id: int) -> Optional[WorkerMovement]:
        return self.repository.get_by_id(movement_id)

    def get_movements_by_date_range(
        self, start_date: date, end_date: date
    ) -> List[WorkerMovement]:
        return self.repository.get_all_by_date(start_date, end_date)

    def create_movement(self, movement_data: WorkerMovementCreate) -> WorkerMovement:
        return self.repository.create(movement_data)

    def update_movement(
        self, movement_id: int, movement_data: WorkerMovementUpdate
    ) -> Optional[WorkerMovement]:
        return self.repository.update(movement_id, movement_data)

    def delete_movement(self, movement_id: int) -> bool:
        return self.repository.delete(movement_id)

    def count_movements_by_filters(
        self, filters: WorkerMovementFilters, allowed_lines: List[int]
    ) -> int:
        """Caso de uso para contar movimientos, filtrado por líneas permitidas."""

        if not allowed_lines:
            return 0
            
        allowed_lines_str = [str(line_id) for line_id in allowed_lines]

        return self.repository.count_by_filters(filters, allowed_lines_str)

    def get_movements_paginated_by_filters(
        self, filters: WorkerMovementPagination, allowed_lines: List[int]
    ) -> WorkerMovementPaginatedResponse:
        """Caso de uso para obtener movimientos paginados con metadatos, filtrado por líneas permitidas."""
        
        if not allowed_lines:
            return {
                "total_records": 0,
                "total_pages": 0,
                "page": filters.page,
                "page_size": filters.page_size,
                "data": [],
            }
        
        allowed_lines_str = [str(line_id) for line_id in allowed_lines]

        data, total_records = self.repository.get_paginated_by_filters(
            filters=filters, 
            page=filters.page, 
            page_size=filters.page_size,
            allowed_lines=allowed_lines_str  # <-- Nuevo argumento
        )
        
        total_pages = ceil(total_records / filters.page_size) if total_records > 0 else 0

        return {
            "total_records": total_records,
            "total_pages": total_pages,
            "page": filters.page,
            "page_size": filters.page_size,
            "data": data, # Lista de entidades de dominio
        }

class RefMotivoUseCases:
    def __init__(self, repository: IRefMotivoRepository):
        self.repository = repository
        
    def count_active_motives(self, filters: RefMotivoFilters) -> int:
        """Cuenta el total de motivos activos (el filtro ACTIVO es implícito en el repo)."""
        _, total_records = self.repository.get_paginated_active(page=1, page_size=1)
        return total_records

    def get_active_paginated_motives(self, pagination_params: RefMotivoPagination) -> List[RefMotivo]:
        """Obtiene una lista de motivos activos paginados (solo data)."""
        
        data, _ = self.repository.get_paginated_active(
            page=pagination_params.page, 
            page_size=pagination_params.page_size
        )
        # Solo retornamos la lista de entidades
        return data


class RefDestinoMotivoUseCases:
    def __init__(self, repository: IRefDestinoMotivoRepository):
        self.repository = repository
        
    def count_destinations_by_motivo(self, filters: RefDestinoMotivoFilters) -> int:
        """Cuenta el total de destinos asociados a un id_motivo específico."""
        # Obtenemos el total de registros usando una paginación mínima.
        _, total_records = self.repository.get_paginated_by_motivo(
            id_motivo=filters.id_motivo, 
            page=1, 
            page_size=1
        )
        return total_records

    def get_destinations_paginated_by_motivo(self, pagination_params: RefDestinoMotivoPagination) -> List[RefDestinoMotivo]:
        """Obtiene una lista de destinos paginados por ID de motivo (solo data)."""

        data, _ = self.repository.get_paginated_by_motivo(
            id_motivo=pagination_params.id_motivo, 
            page=pagination_params.page, 
            page_size=pagination_params.page_size
        )
        # Solo retornamos la lista de entidades
        return data