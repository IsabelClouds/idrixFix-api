from math import ceil

from _decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Dict, Any

from src.modules.lineas_entrada_salida_service.src.infrastructure.api.schemas.lineas_salida import PanzaRequest
from src.modules.auth_service.src.application.use_cases.audit_use_case import AuditUseCase
from src.modules.lineas_entrada_salida_service.src.application.ports.lineas_entrada import ILineasEntradaRepository
from src.modules.lineas_entrada_salida_service.src.domain.entities import LineasEntrada
from src.modules.lineas_entrada_salida_service.src.infrastructure.api.schemas.lineas_entrada import \
    LineasEntradaPaginatedResponse, LineasEntradaUpdate, LineasEntradaResponse
from src.modules.lineas_entrada_salida_service.src.infrastructure.api.schemas.lineas_shared import \
    LineasPagination, LineasFilters
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

        nuevo_valor_parrilla = str(int(linea.codigo_parrilla or 0) + valor)
        nuevo_valor_secuencia = str(int(linea.codigo_secuencia or 0) + valor)
        updated = self.lineas_entrada_repository.update_codigo_parrilla(linea_id, linea_num, nuevo_valor_parrilla, nuevo_valor_secuencia)
        self.audit_use_case.log_action(
            accion="UPDATE",
            user_id=user_data.get("user_id"),
            modelo=self._modelo_auditoria(linea_num),
            entidad_id=linea_id,
            datos_nuevos=LineasEntradaResponse.model_validate(updated).model_dump(mode="json"),
            datos_anteriores=LineasEntradaResponse.model_validate(linea).model_dump(mode="json")
        )
        return updated

    def agregar_panza(self, linea_num: int, data: PanzaRequest, user_data: Dict[str, Any]) -> int:
        if data.peso_kg <= 0:
            raise ValidationError("El peso debe ser mayor que cero.")

        # Obtener registros
        lineas = self.lineas_entrada_repository.get_all_by_filters(
            filters=LineasFilters(fecha=data.fecha, lote=data.lote),
            linea_num=linea_num
        )
        if not lineas:
            raise NotFoundError("No se encontraron registros con los filtros proporcionados.")

        peso_panza_dec = Decimal(str(data.peso_kg))

        items_para_actualizar = []
        datos_anteriores = {}

        for linea in lineas:
            peso_dec = Decimal(str(linea.peso_kg))
            nuevo_peso = float(
                (peso_dec + peso_panza_dec).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
            )

            datos_anteriores[linea.id] = LineasEntradaResponse.model_validate(linea).model_dump(mode="json")

            items_para_actualizar.append({
                "linea_id": linea.id,
                "linea_num": linea_num,
                "nuevo_peso": nuevo_peso
            })

        lineas_actualizadas = self.lineas_entrada_repository.agregar_panzas(items_para_actualizar)

        logs_batch = []
        for updated_linea in lineas_actualizadas:
            logs_batch.append({
                "accion": "UPDATE",
                "modelo": self._modelo_auditoria(linea_num),
                "entidad_id": updated_linea.id,
                "datos_nuevos": LineasEntradaResponse.model_validate(updated_linea).model_dump(mode="json"),
                "datos_anteriores": datos_anteriores.get(updated_linea.id)
            })

        self.audit_use_case.log_actions_batch(
            logs=logs_batch,
            user_id=user_data.get("user_id")
        )

        return len(lineas_actualizadas)

    def count_lineas_entrada(self, filters: LineasFilters, linea_num: int) -> int:
        return self.lineas_entrada_repository.count_by_filters(filters, linea_num)