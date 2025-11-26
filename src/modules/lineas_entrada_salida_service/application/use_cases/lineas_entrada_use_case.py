from math import ceil
from typing import Optional, Dict, Any

from src.modules.auth_service.src.application.use_cases.audit_use_case import AuditUseCase
from src.modules.lineas_entrada_salida_service.application.ports.lineas_entrada import ILineasEntradaRepository
from src.modules.lineas_entrada_salida_service.domain.entities import LineasEntrada
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.lineas_entrada import \
    LineasEntradaPaginatedResponse, LineasEntradaUpdate, LineasEntradaResponse
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.lineas_filters import \
    LineasPagination
from src.shared.exceptions import NotFoundError, ValidationError


class LineasEntradaUseCase:
    def __init__(self, lineas_entrada_repository: ILineasEntradaRepository, audit_use_case: AuditUseCase):
        self.lineas_entrada_repository = lineas_entrada_repository
        self.audit_use_case = audit_use_case

    def _numero_en_letras(self, numero: int) -> str:
        mapping = {
            1: "uno",
            2: "dos",
            3: "tres",
            4: "cuatro",
            5: "cinco",
            6: "seis"
        }
        return mapping.get(numero, "desconocido")

    def _modelo_auditoria(self, linea_num: int) -> str:
        return f"reg_linea_{self._numero_en_letras(linea_num)}_entrada"

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

    def update_linea_entrada(self, linea_id: int, linea_entrada_data: LineasEntradaUpdate, linea_num: int, user_data: Dict[str, Any]) -> Optional[LineasEntrada]:
        linea_entrada = self.lineas_entrada_repository.get_by_id(linea_id, linea_num)
        updated_linea_entrada = self.lineas_entrada_repository.update(linea_id, linea_entrada_data, linea_num)
        self.audit_use_case.log_action(
            accion="UPDATE",
            user_id=user_data.get("user_id"),
            modelo=self._modelo_auditoria(linea_num),
            entidad_id=linea_id,
            datos_nuevos=LineasEntradaResponse.model_validate(updated_linea_entrada).model_dump(mode="json"),
            datos_anteriores = LineasEntradaResponse.model_validate(linea_entrada).model_dump(mode="json")
        )
        return updated_linea_entrada

    def remove_linea_entrada(self, linea_id: int, linea_num:int, user_data: Dict[str, Any]) -> bool:
        linea_entrada = self.lineas_entrada_repository.get_by_id(linea_id, linea_num)
        if not linea_entrada:
            raise NotFoundError(f"Linea entrada con id={linea_id} no encontrada")

        self.audit_use_case.log_action(
            accion="DELETE",
            user_id=user_data.get("user_id"),
            modelo=self._modelo_auditoria(linea_num),
            entidad_id=linea_id,
            datos_anteriores=LineasEntradaResponse.model_validate(linea_entrada).model_dump(mode="json")
        )

        return self.lineas_entrada_repository.remove(linea_id, linea_num)

    def update_codigo_parrilla(self, linea_id: int, linea_num: int, valor: int, user_data: Dict[str, Any]):
        linea = self.lineas_entrada_repository.get_by_id(linea_id, linea_num)

        if valor == 0:
            raise ValidationError("El valor no puede ser cero.")

        nuevo_valor = str(int(linea.codigo_parrilla or 0) + valor)
        updated = self.lineas_entrada_repository.update_codigo_parrilla(linea_id, linea_num, nuevo_valor)
        self.audit_use_case.log_action(
            accion="UPDATE",
            user_id=user_data.get("user_id"),
            modelo=self._modelo_auditoria(linea_num),
            entidad_id=linea_id,
            datos_nuevos=LineasEntradaResponse.model_validate(updated).model_dump(mode="json"),
            datos_anteriores=LineasEntradaResponse.model_validate(linea).model_dump(mode="json")
        )
        return updated