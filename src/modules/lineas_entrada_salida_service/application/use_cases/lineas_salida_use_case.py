from decimal import Decimal, ROUND_HALF_UP
from math import ceil
from typing import Optional, Dict, Any

from src.modules.auth_service.src.application.use_cases.audit_use_case import AuditUseCase
from src.modules.lineas_entrada_salida_service.application.ports.control_tara import IControlTaraRepository
from src.modules.lineas_entrada_salida_service.application.ports.lineas_salida import ILineasSalidaRepository
from src.modules.lineas_entrada_salida_service.domain.entities import LineasSalida
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.lineas_filters import LineasPagination
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.lineas_salida import \
    LineasSalidaPaginatedResponse, LineasSalidaUpdate, LineasSalidaResponse
from src.shared.exceptions import NotFoundError, ValidationError


class LineasSalidaUseCase:
    def __init__(self, lineas_salida_repository: ILineasSalidaRepository, control_tara_repository:  IControlTaraRepository, audit_use_case: AuditUseCase):
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

    def update_linea_salida(self, linea_id, linea_salida_data: LineasSalidaUpdate, linea_num: int, user_data: Dict[str, Any]) -> Optional[LineasSalida]:
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

    from decimal import Decimal

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
