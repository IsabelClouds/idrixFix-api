from decimal import Decimal, ROUND_HALF_UP
from math import ceil
from typing import Optional, Dict, Any, List

from src.modules.auth_service.src.application.use_cases.audit_use_case import AuditUseCase
from src.modules.lineas_entrada_salida_service.application.ports.control_tara import IControlTaraRepository
from src.modules.lineas_entrada_salida_service.application.ports.lineas_salida import ILineasSalidaRepository
from src.modules.lineas_entrada_salida_service.domain.entities import LineasSalida
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.lineas_shared import LineasPagination, \
    LineasFilters
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.lineas_salida import \
    LineasSalidaPaginatedResponse, LineasSalidaUpdate, LineasSalidaResponse, PanzaRequest
from src.shared.exceptions import NotFoundError, ValidationError


class LineasSalidaUseCase:
    def __init__(self, lineas_salida_repository: ILineasSalidaRepository,
                 control_tara_repository: IControlTaraRepository, audit_use_case: AuditUseCase):
        self.lineas_salida_repository = lineas_salida_repository
        self.control_tara_repository = control_tara_repository
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
        return f"reg_linea_{self._numero_en_letras(linea_num)}_salida"

    def get_lineas_salida_paginated_by_filters(self, filters: LineasPagination,
                                               linea_num: int) -> LineasSalidaPaginatedResponse:
        data, total_records = self.lineas_salida_repository.get_paginated_by_filters(
            filters=filters,
            page=filters.page,
            page_size=filters.page_size,
            linea_num=linea_num
        )

        total_pages = ceil(total_records / filters.page_size) if total_records > 0 else 0

        return {
            "total_records": total_records,
            "total_pages": total_pages,
            "page": filters.page,
            "page_size": filters.page_size,
            "data": data
        }

    def get_linea_salida_by_id(self, linea_id: int, linea_num: int) -> Optional[LineasSalida]:
        return self.lineas_salida_repository.get_by_id(linea_id, linea_num)

    def update_linea_salida(self, linea_id, linea_salida_data: LineasSalidaUpdate, linea_num: int,
                            user_data: Dict[str, Any]) -> Optional[LineasSalida]:
        linea_salida = self.lineas_salida_repository.get_by_id(linea_id, linea_num)
        updated_linea_salida = self.lineas_salida_repository.update(linea_id, linea_salida_data, linea_num)
        self.audit_use_case.log_action(
            accion="UPDATE",
            user_id=user_data.get("user_id"),
            modelo=self._modelo_auditoria(linea_num),
            entidad_id=linea_id,
            datos_nuevos=LineasSalidaResponse.model_validate(updated_linea_salida).model_dump(mode="json"),
            datos_anteriores=LineasSalidaResponse.model_validate(linea_salida).model_dump(mode="json")
        )

        return updated_linea_salida

    def remove_linea_salida(self, linea_id: int, linea_num: int, user_data: Dict[str, Any]) -> bool:
        linea_salida = self.lineas_salida_repository.get_by_id(linea_id, linea_num)
        if not linea_salida:
            raise NotFoundError(f"Linea entrada con id={linea_id} no encontrada")

        self.audit_use_case.log_action(
            accion="DELETE",
            user_id=user_data.get("user_id"),
            modelo=self._modelo_auditoria(linea_num),
            entidad_id=linea_id,
            datos_anteriores=LineasSalidaResponse.model_validate(linea_salida).model_dump(mode="json")
        )

        return self.lineas_salida_repository.remove(linea_id, linea_num)

    def agregar_tara(self, linea_id: int, linea_num: int, tara_id: int, user_data: Dict[str, Any]) -> Optional[
        LineasSalida]:
        linea = self.lineas_salida_repository.get_by_id(linea_id, linea_num)
        tara = self.control_tara_repository.get_by_id(tara_id)

        # convertir ambos valores a Decimal
        peso = Decimal(str(linea.peso_kg))
        tara_peso = Decimal(str(tara.peso_kg))

        # restar
        nuevo_peso = peso - tara_peso

        if nuevo_peso <= 0:
            raise ValidationError("El peso debe quedar mayor que cero")

        # redondear a máximo 3 decimales
        nuevo_peso = nuevo_peso.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)

        updated_linea_salida = self.lineas_salida_repository.agregar_tara(
            linea_id,
            linea_num,
            float(nuevo_peso)
        )

        self.audit_use_case.log_action(
            accion="UPDATE",
            user_id=user_data.get("user_id"),
            modelo=self._modelo_auditoria(linea_num),
            entidad_id=linea_id,
            datos_nuevos=LineasSalidaResponse.model_validate(updated_linea_salida).model_dump(mode="json"),
            datos_anteriores=LineasSalidaResponse.model_validate(linea).model_dump(mode="json")
        )

        return updated_linea_salida

    def update_codigo_parrilla(self, linea_id: int, linea_num: int, valor: int, user_data: Dict[str, Any]):
        linea = self.lineas_salida_repository.get_by_id(linea_id, linea_num)

        if valor == 0:
            raise ValidationError("El valor no puede ser cero.")

        nuevo_valor_parrilla = str(int(linea.codigo_parrilla or 0) + valor)
        updated = self.lineas_salida_repository.update_codigo_parrilla(linea_id, linea_num, nuevo_valor_parrilla)
        self.audit_use_case.log_action(
            accion="UPDATE",
            user_id=user_data.get("user_id"),
            modelo=self._modelo_auditoria(linea_num),
            entidad_id=linea_id,
            datos_nuevos=LineasSalidaResponse.model_validate(updated).model_dump(mode="json"),
            datos_anteriores=LineasSalidaResponse.model_validate(linea).model_dump(mode="json")
        )
        return updated

    def count_lineas_salida(self, filters: LineasFilters, linea_num: int) -> int:
        return self.lineas_salida_repository.count_by_filters(filters, linea_num)

    def get_all_by_filters(self, filters: LineasFilters, linea_num: int) -> List[LineasSalida]:
        return self.lineas_salida_repository.get_all_by_filters(filters, linea_num)

    def agregar_panza(self, linea_num: int, data: PanzaRequest, user_data: Dict[str, Any]):
        if data.peso_kg <= 0: raise ValidationError("El peso debe ser mayor que cero.")

        # Obtener TODOS los registros filtrados
        lineas = self.lineas_salida_repository.get_all_by_filters(
            filters=LineasFilters(fecha=data.fecha, lote=data.lote),
            linea_num=linea_num
        )
        if not lineas:
            raise NotFoundError("No se encontraron registros con los filtros proporcionados.")

        peso_panza_dec = Decimal(str(data.peso_kg))
        updated_items = []
        for linea in lineas:
            peso_dec = Decimal(str(linea.peso_kg))
            nuevo_peso = float((peso_dec + peso_panza_dec).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP))
            updated_linea = self.lineas_salida_repository.agregar_panza(linea.id, linea_num, nuevo_peso)

            # Auditoría por registro
            self.audit_use_case.log_action(
                accion="UPDATE",
                user_id=user_data.get("user_id"),
                modelo=self._modelo_auditoria(linea_num),
                entidad_id=linea.id,
                datos_nuevos=LineasSalidaResponse.model_validate(updated_linea).model_dump(mode="json"),
                datos_anteriores=LineasSalidaResponse.model_validate(linea).model_dump(mode="json")
            )

            # Agregar a la lista de resultados
            updated_items.append(updated_linea)

        return updated_items
