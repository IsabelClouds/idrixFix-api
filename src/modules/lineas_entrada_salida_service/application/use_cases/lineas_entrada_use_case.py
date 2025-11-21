from math import ceil
from typing import Optional

from src.modules.lineas_entrada_salida_service.application.ports.lineas_entrada import ILineasEntradaRepository
from src.modules.lineas_entrada_salida_service.domain.entities import LineasEntrada
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.lineas_entrada import \
    LineasEntradaPaginatedResponse, LineasEntradaUpdate
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.lineas_filters import \
    LineasPagination
from src.shared.exceptions import NotFoundError


class LineasEntradaUseCase:
    def __init__(self, lineas_entrada_repository: ILineasEntradaRepository):
        self.lineas_entrada_repository = lineas_entrada_repository

    def get_lineas_entrada_paginated_by_filters(self, filters: LineasPagination, linea_num: int) -> LineasEntradaPaginatedResponse:
        data, total_records = self.lineas_entrada_repository.get_paginated_by_filters(
            filters=filters,
            page=filters.page,
            page_size=filters.page_size,
            linea_num=linea_num
        )

        total_pages = ceil(total_records/ filters.page_size) if total_records > 0 else 0

        return {
            "total_records": total_records,
            "total_pages": total_pages,
            "page": filters.page,
            "page_size": filters.page_size,
            "data": data
        }

    def get_linea_entrada_by_id(self, linea_id: int, linea_num: int) -> Optional[LineasEntrada]:
        return self.lineas_entrada_repository.get_by_id(linea_id, linea_num)

    #TODO agregar auditorias
    def update_linea_entrada(self, linea_id: int, linea_entrada_data: LineasEntradaUpdate, linea_num: int) -> Optional[LineasEntrada]:
        updated_linea_entrada = self.lineas_entrada_repository.update(linea_id, linea_entrada_data, linea_num)
        return updated_linea_entrada

    # TODO agregar auditorias
    def remove_linea_entrada(self, linea_id: int, linea_num:int) -> bool:
        linea_entrada = self.lineas_entrada_repository.get_by_id(linea_id, linea_num)
        if not linea_entrada:
            raise NotFoundError(f"Linea entrada con id={linea_id} no encontrada")

        return self.lineas_entrada_repository.remove(linea_id, linea_num)