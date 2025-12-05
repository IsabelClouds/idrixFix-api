import logging

from fastapi import APIRouter, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from src.modules.administracion_service.src.application.use_case.control_lote_asiglinea_use_case import \
    ControlLoteAsiglineaUseCase
from src.modules.administracion_service.src.infrastructure.api.schemas.control_lote_asiglinea import \
    ControlLoteAsiglineaPagination, ControlLoteAsiglineaResponse, ControlLoteAsiglineaUpdate
from src.modules.administracion_service.src.infrastructure.db.repositories.control_lote_asiglinea_repository import \
    ControlLoteAsiglineaRepository
from src.shared.base import get_db
from src.shared.common.responses import success_response, error_response
from src.shared.exceptions import RepositoryError

router = APIRouter()


def get_control_lote_asiglinea_use_case(
        db: Session = Depends(get_db)
) -> ControlLoteAsiglineaUseCase:
    return ControlLoteAsiglineaUseCase(
        control_lote_asiglinea_repository=ControlLoteAsiglineaRepository(db)
    )


@router.get("/{lote_id}", response_model=ControlLoteAsiglineaResponse, status_code=status.HTTP_200_OK)
def get_lote_by_id(
        lote_id: int,
        use_case: ControlLoteAsiglineaUseCase = Depends(get_control_lote_asiglinea_use_case)
):
    try:
        response = use_case.get_lote_by_id(lote_id)
        return success_response(
            data=response,
            message="Lote actualizado"
        )
    except RepositoryError as e:
        return error_response(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/paginated", status_code=status.HTTP_200_OK)
def get_all_lote_asiglineas(
        pagination_params: ControlLoteAsiglineaPagination,
        use_case: ControlLoteAsiglineaUseCase = Depends(get_control_lote_asiglinea_use_case),
):
    try:
        pagination_result = use_case.get_lote_asiglineas_paginated_by_filters(pagination_params)

        response_data = [
            ControlLoteAsiglineaResponse.model_validate(d).model_dump(mode="json")
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
            message="Lotes Obtenidos"
        )

    except RepositoryError as e:
        return error_response(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.patch("/{lote_id}", response_model=ControlLoteAsiglineaResponse, status_code=status.HTTP_200_OK)
def update_lote_asiglinea(
        lote_id: int,
        data: ControlLoteAsiglineaUpdate,
        use_case: ControlLoteAsiglineaUseCase = Depends(get_control_lote_asiglinea_use_case)
):
    response = use_case.update_lote_asiglinea(data, lote_id)
    return success_response(
        data=response,
        message="Lote actualizado"
    )


@router.delete("/{lote_id}", status_code=status.HTTP_200_OK)
def remove_lote(
        lote_id: int,
        use_case: ControlLoteAsiglineaUseCase = Depends(get_control_lote_asiglinea_use_case)
):
    try:
        use_case.remove_lote(lote_id)
        return success_response(
            data=f"lote con id {lote_id} eliminado",
            message="Lote eliminado correctamente"
        )
    except RepositoryError as e:
        return error_response(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
