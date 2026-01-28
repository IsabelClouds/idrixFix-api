from decimal import Decimal, ROUND_HALF_UP
from math import ceil
from typing import Optional, Dict, Any, List
import logging

from src.modules.lineas_entrada_salida_service.src.application.ports.control_miga import IControlMigaRepository
from src.modules.lineas_entrada_salida_service.src.infrastructure.api.schemas.lineas_salida import \
    LineasSalidaMigaResponse, MigaResponse, LineasSalidaMigaPaginatedResponse, MigaRequest
from src.modules.auth_service.src.application.use_cases.audit_use_case import AuditUseCase
from src.modules.lineas_entrada_salida_service.src.application.ports.control_tara import IControlTaraRepository
from src.modules.lineas_entrada_salida_service.src.application.ports.lineas_salida import ILineasSalidaRepository
from src.modules.lineas_entrada_salida_service.src.domain.entities import LineasSalida
from src.modules.lineas_entrada_salida_service.src.infrastructure.api.schemas.lineas_shared import LineasPagination, \
    LineasFilters
from src.modules.lineas_entrada_salida_service.src.infrastructure.api.schemas.lineas_salida import \
    LineasSalidaPaginatedResponse, LineasSalidaUpdate, LineasSalidaResponse, PanzaRequest
from src.shared.exceptions import NotFoundError, ValidationError


class LineasSalidaUseCase:
    def __init__(self, lineas_salida_repository: ILineasSalidaRepository,
                 control_tara_repository: IControlTaraRepository, audit_use_case: AuditUseCase, control_miga_repository: IControlMigaRepository):
        self.lineas_salida_repository = lineas_salida_repository
        self.control_tara_repository = control_tara_repository
        self.audit_use_case = audit_use_case
        self.control_miga_repository = control_miga_repository

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

    def _empty_response(self, filters: LineasPagination) -> LineasSalidaMigaPaginatedResponse:
        return {
            "total_records": 0,
            "total_pages": 0,
            "page": filters.page,
            "page_size": filters.page_size,
            "data": []
        }

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

    def get_lineas_salida_miga_paginated_by_filters(self, filters: LineasPagination, linea_num: int) -> LineasSalidaMigaPaginatedResponse:
        lineas, total_records = self.lineas_salida_repository.get_paginated_by_filters(
            filters=filters,
            page=filters.page,
            page_size=filters.page_size,
            linea_num=linea_num
        )

        if not lineas:
            return self._empty_response(filters)

        total_pages = ceil(total_records / filters.page_size) if total_records > 0 else 0

        registro_ids = [linea.id for linea in lineas]
        migas_list = self.control_miga_repository.get_by_registros_bulk(
            linea_num=linea_num,
            registros=registro_ids
        )

        migas_map = {miga.registro: miga for miga in migas_list}

        data_response: list[LineasSalidaMigaResponse] = []

        for linea in lineas:
            miga = migas_map.get(linea.id)

            data_response.append(
                LineasSalidaMigaResponse(
                    id=linea.id,
                    fecha_p=linea.fecha_p,
                    fecha=linea.fecha,
                    peso_kg=linea.peso_kg,
                    codigo_bastidor=linea.codigo_bastidor,
                    p_lote=linea.p_lote,
                    codigo_parrilla=linea.codigo_parrilla,
                    codigo_obrero=linea.codigo_obrero,
                    guid=linea.guid,
                    p_miga=miga.p_miga if miga else 0.0,
                    porcentaje=miga.porcentaje if miga else 0.0
                )
            )

        return {
            "total_records": total_records,
            "total_pages": total_pages,
            "page": filters.page,
            "page_size": filters.page_size,
            "data": data_response
        }

    def get_lineas_salida_miga_paginated_by_filters_report(
            self,
            filters: LineasPagination,
            linea_num: int
    ) -> LineasSalidaMigaPaginatedResponse:

        lineas, total_records = self.lineas_salida_repository.get_paginated_by_filters(
            filters=filters,
            page=filters.page,
            page_size=filters.page_size,
            linea_num=linea_num
        )

        if not lineas:
            return self._empty_response(filters)

        registro_ids = [linea.id for linea in lineas]

        migas_list = self.control_miga_repository.get_by_registros_bulk(
            linea_num=linea_num,
            registros=registro_ids
        )

        migas_map = {miga.registro: miga for miga in migas_list}

        data_response: list[LineasSalidaMigaResponse] = []

        for linea in lineas:
            miga = migas_map.get(linea.id)

            if miga:
                data_response.append(
                    LineasSalidaMigaResponse(
                        id=linea.id,
                        fecha_p=linea.fecha_p,
                        fecha=linea.fecha,
                        peso_kg=linea.peso_kg,
                        codigo_bastidor=linea.codigo_bastidor,
                        p_lote=linea.p_lote,
                        codigo_parrilla=linea.codigo_parrilla,
                        codigo_obrero=linea.codigo_obrero,
                        guid=linea.guid,
                        p_miga=miga.p_miga,
                        porcentaje=miga.porcentaje
                    )
                )

        actual_count = len(data_response)

        return {
            "total_records": actual_count,
            "total_pages": ceil(total_records / filters.page_size),
            "page": filters.page,
            "page_size": filters.page_size,
            "data": data_response
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

    def agregar_panza(self, linea_num: int, data: PanzaRequest, user_data: Dict[str, Any]) -> int:
        if data.peso_kg <= 0:
            raise ValidationError("El peso debe ser mayor que cero.")

        # Obtener registros
        lineas = self.lineas_salida_repository.get_all_by_filters(
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

            datos_anteriores[linea.id] = LineasSalidaResponse.model_validate(linea).model_dump(mode="json")

            items_para_actualizar.append({
                "linea_id": linea.id,
                "linea_num": linea_num,
                "nuevo_peso": nuevo_peso
            })

        lineas_actualizadas = self.lineas_salida_repository.agregar_panzas(items_para_actualizar)

        logs_batch = []
        for updated_linea in lineas_actualizadas:
            logs_batch.append({
                "accion": "UPDATE",
                "modelo": self._modelo_auditoria(linea_num),
                "entidad_id": updated_linea.id,
                "datos_nuevos": LineasSalidaResponse.model_validate(updated_linea).model_dump(mode="json"),
                "datos_anteriores": datos_anteriores.get(updated_linea.id)
            })

        self.audit_use_case.log_actions_batch(
            logs=logs_batch,
            user_id=user_data.get("user_id")
        )

        return len(lineas_actualizadas)

    def update_lote_batch(self, linea_num: int, ids: list[int], lote: str, user_data: Dict[str, Any]) -> int:

        if not lote:
            raise ValidationError("El lote no puede estar vacío.")

        lineas_anteriores = {
            l.id: LineasSalidaResponse.model_validate(l).model_dump(mode="json")
            for l in self.lineas_salida_repository.get_all_by_filters(
                LineasFilters(),
                linea_num
            )
            if l.id in ids
        }

        updated = self.lineas_salida_repository.update_lote_by_ids(
            linea_num=linea_num,
            ids=ids,
            lote=lote
        )

        logs = []
        for linea in updated:

            logs.append({
                "accion": "UPDATE",
                "modelo": self._modelo_auditoria(linea_num),
                "entidad_id": linea.id,
                "datos_nuevos": LineasSalidaResponse.model_validate(linea).model_dump(mode="json"),
                "datos_anteriores": lineas_anteriores.get(linea.id)
            })

        self.audit_use_case.log_actions_batch(
            logs=logs,
            user_id=user_data.get("user_id")
        )

        return len(updated)

    def create_miga(self, linea_num: int, data: MigaRequest, user_data: Dict[str, Any]) -> LineasSalidaMigaResponse:
        if data is None:
            raise ValidationError("Los datos de la miga no pueden estar vacios")

        if data.p_miga is None:
            raise ValidationError("El campo p_miga no puede ser nulo")

        if data.linea_id is None:
            raise ValidationError("El campo linea_id no puede ser nulo")

        miga = self.control_miga_repository.get_by_registro(linea_num, data.linea_id)

        if miga:
            raise ValidationError("La miga ya existe")

        linea_registro = self.lineas_salida_repository.get_by_id(data.linea_id,linea_num)

        if linea_registro is None:
            raise NotFoundError("La línea de salida no existe")

        if data.tara_id is not None:
            tara = self.control_tara_repository.get_by_id(data.tara_id)
            if tara is not None:
                porcentaje = round(
                    ((linea_registro.peso_kg - tara.peso_kg) -
                     (data.p_miga - tara.peso_kg)) / linea_registro.peso_kg,
                    3
                )
            else:
                raise NotFoundError("La tara no existe")
        else:
            porcentaje = round(
                (linea_registro.peso_kg - data.p_miga) / linea_registro.peso_kg,
                3
            )

        nueva_miga = self.control_miga_repository.create(linea_num, data.linea_id, data.p_miga, porcentaje)

        miga_response = MigaResponse(
            id = nueva_miga.id,
            linea = nueva_miga.linea,
            registro = nueva_miga.registro,
            p_miga = nueva_miga.p_miga,
            porcentaje = nueva_miga.porcentaje,
        )

        self.audit_use_case.log_action(
            accion="CREATE",
            user_id=user_data.get("user_id"),
            modelo="control_miga",
            entidad_id=nueva_miga.id,
            datos_nuevos=MigaResponse.model_validate(miga_response).model_dump(mode="json")
        )

        response = LineasSalidaMigaResponse(
            id = linea_registro.id,
            fecha_p = linea_registro.fecha_p,
            fecha = linea_registro.fecha,
            peso_kg = linea_registro.peso_kg,
            codigo_bastidor = linea_registro.codigo_bastidor,
            p_lote = linea_registro.p_lote,
            codigo_parrilla = linea_registro.codigo_parrilla,
            codigo_obrero = linea_registro.codigo_obrero,
            guid = linea_registro.guid,
            p_miga = nueva_miga.p_miga,
            porcentaje = nueva_miga.porcentaje,
        )

        return response

    def update_miga(self, linea_num: int, data: MigaRequest, user_data: Dict[str, Any]) -> LineasSalidaMigaResponse:
        if data is None:
            raise ValidationError("Los datos de la miga no pueden estar vacios")

        if data.p_miga is None:
            raise ValidationError("El campo p_miga no puede ser nulo")

        if data.linea_id is None:
            raise ValidationError("El campo linea_id no puede ser nulo")

        miga = self.control_miga_repository.get_by_registro(linea_num, data.linea_id)

        if miga is None:
            raise NotFoundError("La miga no existe")

        linea_registro = self.lineas_salida_repository.get_by_id(data.linea_id, linea_num)

        if linea_registro is None:
            raise NotFoundError("La línea de salida no existe")

        if data.tara_id is not None:
            tara = self.control_tara_repository.get_by_id(data.tara_id)
            if tara is not None:
                porcentaje = round(
                    ((linea_registro.peso_kg - tara.peso_kg) -
                     (data.p_miga - tara.peso_kg)) / linea_registro.peso_kg,
                    3
                )
            else:
                raise NotFoundError("La tara no existe")
        else:
            porcentaje = round(
                (linea_registro.peso_kg - data.p_miga) / linea_registro.peso_kg,
                3
            )

        miga_actualizada = self.control_miga_repository.update(miga.id, data.p_miga, porcentaje)

        miga_actualizada = MigaResponse(
            id = miga_actualizada.id,
            linea = miga_actualizada.linea,
            registro = miga_actualizada.registro,
            p_miga = miga_actualizada.p_miga,
            porcentaje = miga_actualizada.porcentaje,
        )

        miga_anterior = MigaResponse(
            id = miga.id,
            linea = miga.linea,
            registro = miga.registro,
            p_miga = miga.p_miga,
            porcentaje = miga.porcentaje,
        )

        self.audit_use_case.log_action(
            accion="UPDATE",
            user_id=user_data.get("user_id"),
            modelo="control_miga",
            entidad_id=miga.id,
            datos_nuevos=MigaResponse.model_validate(miga_actualizada).model_dump(mode="json"),
            datos_anteriores=MigaResponse.model_validate(miga_anterior).model_dump(mode="json"),
        )

        response = LineasSalidaMigaResponse(
            id = linea_registro.id,
            fecha_p = linea_registro.fecha_p,
            fecha = linea_registro.fecha,
            peso_kg = linea_registro.peso_kg,
            codigo_bastidor = linea_registro.codigo_bastidor,
            p_lote = linea_registro.p_lote,
            codigo_parrilla = linea_registro.codigo_parrilla,
            codigo_obrero = linea_registro.codigo_obrero,
            guid = linea_registro.guid,
            p_miga = miga_actualizada.p_miga,
            porcentaje = miga_actualizada.porcentaje,
        )

        return response


