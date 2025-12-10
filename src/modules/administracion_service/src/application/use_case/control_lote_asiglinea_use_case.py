from math import ceil
from typing import Optional

from src.modules.administracion_service.src.application.ports.control_lote_asiglinea import \
    IControlLoteAsiglineaRepository
from src.modules.administracion_service.src.application.ports.tipo_limpieza import ITipoLimpiezaRepository
from src.modules.administracion_service.src.domain.entities import ControlLoteAsiglinea
from src.modules.administracion_service.src.infrastructure.api.schemas.control_lote_asiglinea import \
    ControlLoteAsiglineaPagination, ControlLoteAsiglineaResponse, ControlLoteAsiglineaUpdate
from src.shared.exceptions import NotFoundError, ValidationError


class ControlLoteAsiglineaUseCase:
    def __init__(self, control_lote_asiglinea_repository: IControlLoteAsiglineaRepository, tipo_limpieza_repository: ITipoLimpiezaRepository):
        self.control_lote_asiglinea_repository = control_lote_asiglinea_repository
        self.tipo_limpieza_repository = tipo_limpieza_repository

    def _map_to_response(self, lote: ControlLoteAsiglinea) -> ControlLoteAsiglineaResponse:
        tipo_limpieza_obj = None
        if lote.tipo_limpieza is not None:
            tipo_limpieza_obj = self.tipo_limpieza_repository.get_by_id(lote.tipo_limpieza)

        return ControlLoteAsiglineaResponse(
            id=lote.id,
            fecha_p=lote.fecha_p,
            lote=lote.lote,
            linea=lote.linea,
            estado=lote.estado,
            fecha_asig=lote.fecha_asig,
            tipo_limpieza=tipo_limpieza_obj,
            turno=lote.turno
        )

    def get_lote_asiglineas_paginated_by_filters(self, paginated_filters: ControlLoteAsiglineaPagination) -> dict:
        data, total_records = self.control_lote_asiglinea_repository.get_paginated_by_filters(paginated_filters)

        mapped_data = [self._map_to_response(lote) for lote in data]

        total_pages = ceil(total_records / paginated_filters.page_size) if total_records > 0 else 0

        return {
            "total_records": total_records,
            "total_pages": total_pages,
            "page": paginated_filters.page,
            "page_size": paginated_filters.page_size,
            "data": mapped_data
        }

    def update_lote_asiglinea(self, data: ControlLoteAsiglineaUpdate, id: int) -> ControlLoteAsiglineaResponse:
        exists = self.control_lote_asiglinea_repository.exists_by_id(id)
        if not exists:
            raise NotFoundError(f"No se encontró el lote con id {id}")

        if not data.lote or data.lote.strip() == "":
            raise ValidationError("El campo lote no puede estar vacío")

        updated_lote = self.control_lote_asiglinea_repository.update(data, id)
        return self._map_to_response(updated_lote)

    def get_lote_by_id(self, id: int) -> ControlLoteAsiglineaResponse:
        lote = self.control_lote_asiglinea_repository.get_by_id(id)
        if not lote:
            raise NotFoundError("El lote no existe")
        return self._map_to_response(lote)

    def remove_lote(self, id: int) -> bool:
        exists = self.control_lote_asiglinea_repository.exists_by_id(id)
        if not exists:
            raise NotFoundError(f"No se encontró el lote con id {id}")

        return self.control_lote_asiglinea_repository.remove(id)