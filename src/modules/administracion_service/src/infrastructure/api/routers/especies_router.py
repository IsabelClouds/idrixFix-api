from fastapi import APIRouter, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from src.modules.administracion_service.src.application.use_case.especies_use_case import EspeciesUseCase
from src.modules.administracion_service.src.infrastructure.api.schemas.especies import EspeciesResponse, \
    EspeciesRequest, EspeciesPaginated
from src.modules.administracion_service.src.infrastructure.db.repositories.especies_repository import EspeciesRepository
from src.shared.base import get_db
from src.shared.common.responses import success_response

router = APIRouter()


def get_especies_use_case(
        db: Session = Depends(get_db)
) -> EspeciesUseCase:
    return EspeciesUseCase(
        especies_repository=EspeciesRepository(db)
    )


@router.post("/paginated", status_code=status.HTTP_200_OK)
def get_all_especies_paginated(
        pagination_params: EspeciesPaginated,
        use_case: EspeciesUseCase = Depends(get_especies_use_case)
):
    pagination_result = use_case.get_all_especies_paginated(pagination_params)
    response_data = [
        EspeciesResponse.model_validate(d).model_dump(mode="json")
        for d in pagination_result["data"]
    ]

    response_data_with_meta = {
        "total_records": pagination_result["total_records"],
        "total_pages": pagination_result["total_pages"],
        "page": pagination_result["page"],
        "page_size": pagination_result["page_size"],
        "data": response_data,
    }

    return success_response(
        data=response_data_with_meta,
        message="Especies Obtenidas",
    )


@router.get("/{especie_id}", status_code=status.HTTP_200_OK, response_model=EspeciesResponse)
def get_especie_by_id(
        especie_id: int,
        use_case: EspeciesUseCase = Depends(get_especies_use_case)
):
    response = use_case.get_especie_by_id(especie_id)
    return success_response(
        data=EspeciesResponse.model_validate(response).model_dump(mode="json"),
        message="Especie obtenida",
    )


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=EspeciesResponse)
def create_especie(
        data: EspeciesRequest,
        use_case: EspeciesUseCase = Depends(get_especies_use_case)
):
    response = use_case.create_especie(data)
    return success_response(
        data=EspeciesResponse.model_validate(response).model_dump(mode="json"),
        message="Especie creada"
    )


@router.patch("/{especie_id}", status_code=status.HTTP_200_OK, response_model=EspeciesResponse)
def update_especie(
        especie_id: int,
        data: EspeciesRequest,
        use_case: EspeciesUseCase = Depends(get_especies_use_case)
):
    response = use_case.update_especie(especie_id, data)
    return success_response(
        data=EspeciesResponse.model_validate(response).model_dump(mode="json"),
        message="Especie actualizada correctamente"
    )
