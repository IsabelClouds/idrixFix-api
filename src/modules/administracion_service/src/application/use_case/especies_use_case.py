from math import ceil
from typing import Dict, Any

from src.modules.administracion_service.src.application.ports.especies import IEspeciesRepository
from src.modules.administracion_service.src.infrastructure.api.schemas.especies import EspeciesResponse, \
    EspeciesRequest, EspeciesPaginated
from src.modules.auth_service.src.application.use_cases.audit_use_case import AuditUseCase
from src.shared.exceptions import NotFoundError, AlreadyExistsError, ValidationError


class EspeciesUseCase:
    def __init__(self, especies_repository: IEspeciesRepository, audit_use_case: AuditUseCase):
        self.especies_repository = especies_repository
        self.audit_use_case = audit_use_case

    def get_all_especies_paginated(self, pagination: EspeciesPaginated):
        data, total_records = self.especies_repository.get_all_paginated(pagination)

        total_pages = ceil(total_records / pagination.page_size) if total_records > 0 else 0

        return {
            "total_records": total_records,
            "total_pages": total_pages,
            "page": pagination.page,
            "page_size": pagination.page_size,
            "data": [
                EspeciesResponse(
                    especie_id=e.especie_id,
                    especie_nombre=e.especie_nombre,
                    especie_familia=e.especie_familia,
                    especie_kilos_horas=e.especie_kilos_horas,
                    especies_kilos_horas_media=e.especies_kilos_horas_media,
                    especies_kilos_horas_doble=e.especies_kilos_horas_doble
                )
                for e in data
            ]
        }

    def get_especie_by_id(self, id: int) -> EspeciesResponse:
        especie = self.especies_repository.get_by_id(id)
        if not especie:
            raise NotFoundError("La especie no existe")
        return EspeciesResponse(
            especie_id=especie.especie_id,
            especie_nombre=especie.especie_nombre,
            especie_familia=especie.especie_familia,
            especie_kilos_horas=especie.especie_kilos_horas,
            especies_kilos_horas_media=especie.especies_kilos_horas_media,
            especies_kilos_horas_doble=especie.especies_kilos_horas_doble
        )

    def create_especie(self, data: EspeciesRequest, user_data: Dict[str, Any]) -> EspeciesResponse:
        exists = self.especies_repository.exists_by_nombre(data.especie_nombre)
        if exists:
            raise AlreadyExistsError("Ya existe una especie con este nombre")
        especie = self.especies_repository.create(data)

        response = EspeciesResponse(
            especie_id=especie.especie_id,
            especie_nombre=especie.especie_nombre,
            especie_familia=especie.especie_familia,
            especie_kilos_horas=especie.especie_kilos_horas,
            especies_kilos_horas_media=especie.especies_kilos_horas_media,
            especies_kilos_horas_doble=especie.especies_kilos_horas_doble
        )
        self.audit_use_case.log_action(
            accion="CREATE",
            user_id=user_data.get("user_id"),
            modelo="fm_especies",
            entidad_id=response.especie_id,
            datos_nuevos=EspeciesResponse.model_validate(response).model_dump(mode="json")
        )
        return response

    def update_especie(self, id: int, data: EspeciesRequest, user_data: Dict[str, Any]) -> EspeciesResponse:
        exists = self.especies_repository.exists_by_id(id)
        if not exists:
            raise NotFoundError("La especie no existe")

        exists_by_nombre = self.especies_repository.exists_by_nombre(data.especie_nombre)

        if exists_by_nombre:
            raise AlreadyExistsError("Ya existe una especie con este nombre")

        especie_anterior = self.get_especie_by_id(id)
        especie_anterior_response = EspeciesResponse(
            especie_id=especie_anterior.especie_id,
            especie_nombre=especie_anterior.especie_nombre,
            especie_familia=especie_anterior.especie_familia,
            especie_kilos_horas=especie_anterior.especie_kilos_horas,
            especies_kilos_horas_media=especie_anterior.especies_kilos_horas_media,
            especies_kilos_horas_doble=especie_anterior.especies_kilos_horas_doble
        )

        updated_especie = self.especies_repository.update(data, id)
        updated_especie_response = EspeciesResponse(
            especie_id=updated_especie.especie_id,
            especie_nombre=updated_especie.especie_nombre,
            especie_familia=updated_especie.especie_familia,
            especie_kilos_horas=updated_especie.especie_kilos_horas,
            especies_kilos_horas_media=updated_especie.especies_kilos_horas_media,
            especies_kilos_horas_doble=updated_especie.especies_kilos_horas_doble
        )

        self.audit_use_case.log_action(
            accion="UPDATE",
            user_id=user_data.get("user_id"),
            modelo="fm_especies",
            entidad_id=id,
            datos_nuevos=EspeciesResponse.model_validate(updated_especie_response).model_dump(mode="json"),
            datos_anteriores=EspeciesResponse.model_validate(especie_anterior_response).model_dump(mode="json")
        )

        return updated_especie_response
