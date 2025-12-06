from math import ceil
from typing import Optional

from src.modules.administracion_service.src.application.ports.control_lote_asiglinea import \
    IControlLoteAsiglineaRepository
from src.modules.administracion_service.src.domain.entities import ControlLoteAsiglinea
from src.modules.administracion_service.src.infrastructure.api.schemas.control_lote_asiglinea import \
    ControlLoteAsiglineaPagination, ControlLoteAsiglineaResponse, ControlLoteAsiglineaUpdate
from src.shared.exceptions import NotFoundError


class ControlLoteAsiglineaUseCase:
    def __init__(self, control_lote_asiglinea_repository: IControlLoteAsiglineaRepository):
        self.control_lote_asiglinea_repository = control_lote_asiglinea_repository

    def get_lote_asiglineas_paginated_by_filters(self, paginated_filters: ControlLoteAsiglineaPagination) -> ControlLoteAsiglineaResponse:
        data, total_records = self.control_lote_asiglinea_repository.get_paginated_by_filters(paginated_filters)

        total_pages = ceil(total_records/paginated_filters.page_size) if total_records > 0 else 0

        return {
            "total_records": total_records,
            "total_pages": total_pages,
            "page": paginated_filters.page,
            "page_size": paginated_filters.page_size,
            "data": data
        }

    def update_lote_asiglinea(self, data: ControlLoteAsiglineaUpdate, id: int) -> Optional[ControlLoteAsiglinea]:
        exists = self.control_lote_asiglinea_repository.exists_by_id(id)
        if not exists:
            raise NotFoundError(f"No se encontró el lote con id {id}")

        return self.control_lote_asiglinea_repository.update(data, id)

    def get_lote_by_id(self, id: int) -> Optional[ControlLoteAsiglinea]:
        lote = self.control_lote_asiglinea_repository.get_by_id(id)
        if not lote:
            raise NotFoundError("El lote no existe")
        return lote

    def remove_lote(self, id: int) -> bool:
        exists = self.control_lote_asiglinea_repository.exists_by_id(id)
        if not exists:
            raise NotFoundError(f"No se encontró el lote con id {id}")

        return self.control_lote_asiglinea_repository.remove(id)