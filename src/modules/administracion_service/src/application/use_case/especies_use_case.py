from math import ceil

from src.modules.administracion_service.src.application.ports.especies import IEspeciesRepository
from src.modules.administracion_service.src.infrastructure.api.schemas.especies import EspeciesResponse, \
    EspeciesRequest, EspeciesPaginated
from src.shared.exceptions import NotFoundError, AlreadyExistsError


class EspeciesUseCase:
    def __init__(self, especies_repository: IEspeciesRepository):
        self.especies_repository = especies_repository

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

    def create_especie(self, data: EspeciesRequest) -> EspeciesResponse:
        exists = self.especies_repository.exists_by_nombre(data.especie_nombre)
        if exists:
            raise AlreadyExistsError("Ya existe un area con este nombre")
        especie = self.especies_repository.create(data)
        return EspeciesResponse(
            especie_id=especie.especie_id,
            especie_nombre=especie.especie_nombre,
            especie_familia=especie.especie_familia,
            especie_kilos_horas=especie.especie_kilos_horas,
            especies_kilos_horas_media=especie.especies_kilos_horas_media,
            especies_kilos_horas_doble=especie.especies_kilos_horas_doble
        )

    def update_especie(self, id: int, data: EspeciesRequest) -> EspeciesResponse:
        exists = self.especies_repository.exists_by_id(id)
        if not exists:
            raise NotFoundError("La especie no existe")

        updated_especie = self.especies_repository.update(data, id)

        return EspeciesResponse(
            especie_id=updated_especie.especie_id,
            especie_nombre=updated_especie.especie_nombre,
            especie_familia=updated_especie.especie_familia,
            especie_kilos_horas=updated_especie.especie_kilos_horas,
            especies_kilos_horas_media=updated_especie.especies_kilos_horas_media,
            especies_kilos_horas_doble=updated_especie.especies_kilos_horas_doble
        )
