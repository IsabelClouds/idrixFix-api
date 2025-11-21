from math import ceil
from typing import Optional

from src.modules.lineas_entrada_salida_service.application.ports.lineas_salida import ILineasSalidaRepository
from src.modules.lineas_entrada_salida_service.domain.entities import LineasSalida
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.lineas_filters import LineasPagination
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.lineas_salida import \
    LineasSalidaPaginatedResponse
from src.shared.exceptions import NotFoundError


class LineasSalidaUseCase:
    def __init__(self, lineas_salida_repository: ILineasSalidaRepository):
        self.lineas_salida_repository = lineas_salida_repository

    def get_lineas_salida_paginated_by_filters(self, filters: LineasPagination, linea_num: int) -> LineasSalidaPaginatedResponse:
        data, total_records = self.lineas_salida_repository.get_paginated_by_filters(
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

    def get_linea_salida_by_id(self, linea_id: int, linea_num: int) -> Optional[LineasSalida]:
        return self.lineas_salida_repository.get_by_id(linea_id, linea_num)

    #TODO agregar auditorias
    ##TODO hacer update

    # def update_linea_salida(self, linea_id, linea_salida_data: LineasSalidaUpdate, linea_num: int) -> Optional[LineasSalida]:
    #     updated_linea_salida = self.lineas_salida_repository.update(linea_id, linea_salida_data, linea_num)
    #     return updated_linea_salida

    # TODO agregar auditorias
    def remove_linea_salida(self, linea_id: int, linea_num: int) -> bool:
        linea_salida = self.lineas_salida_repository.get_by_id(linea_id, linea_num)
        if not linea_salida:
            raise NotFoundError(f"Linea entrada con id={linea_id} no encontrada")

        return self.lineas_salida_repository.remove(linea_id, linea_num)