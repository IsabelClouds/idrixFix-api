from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.orm import Session

from src.modules.lineas_entrada_salida_service.application.use_cases.lineas_entrada_use_case import \
    LineasEntradaUseCase
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.lineas_entrada import \
    LineasEntradaResponse, LineasEntradaUpdate, UpdateCodigoParrillaRequest
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.lineas_filters import LineasPagination
from src.modules.lineas_entrada_salida_service.infrastructure.db.repositories.lineas_entrada_repository import \
    LineasEntradaRepository
from src.shared.base import get_db
from src.shared.common.responses import success_response, error_response
from src.shared.exceptions import RepositoryError, NotFoundError

router = APIRouter()


def get_lineas_entrada_use_case(
        db_externa: Session = Depends(get_db)
) -> LineasEntradaUseCase:
    return LineasEntradaUseCase(
        lineas_entrada_repository=LineasEntradaRepository(db_externa)
    )


@router.post("/{linea_num}/paginated", status_code=status.HTTP_200_OK)
def get_all_lineas_entrada(
        pagination_params: LineasPagination,
        linea_num: int = Path(..., ge=1, le=6, description="Número de Línea (1 al 6)"),
        use_case: LineasEntradaUseCase = Depends(get_lineas_entrada_use_case)
):
    try:
        pagination_result = use_case.get_lineas_entrada_paginated_by_filters(
            filters=pagination_params,
            linea_num=linea_num
        )

        response_data = [
            LineasEntradaResponse.model_validate(d).model_dump(mode="json")
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
            message=f"Lineas paginadas de la Línea {linea_num} obtenidas",
        )

    except RepositoryError as e:
        return error_response(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{linea_num}/{linea_id}", response_model=LineasEntradaResponse, status_code=status.HTTP_200_OK)
def get_linea_entrada_by_id(
        linea_id: int,
        use_cases: LineasEntradaUseCase = Depends(get_lineas_entrada_use_case),
        linea_num: int = Path(..., ge=1, le=6, description="Número de Línea (1 al 6)"),

):
    data = use_cases.get_linea_entrada_by_id(linea_id, linea_num)
    if not data:
        return error_response(
            message="Producción linea entrada no encontrada", status_code=status.HTTP_404_NOT_FOUND
        )
    return success_response(
        data=LineasEntradaResponse.model_validate(data).model_dump(mode="json"),
        message="Producción linea entrada obtenida",
    )


@router.patch("/{linea_num}/{linea_id}", response_model=LineasEntradaResponse, status_code=status.HTTP_200_OK)
def update_linea_entrada(
        linea_id: int,
        linea_entrada_data: LineasEntradaUpdate,
        use_cases: LineasEntradaUseCase = Depends(get_lineas_entrada_use_case),
        linea_num: int = Path(..., ge=1, le=6, description="Número de Línea (1 al 6)")
):
    try:
        updated_data = use_cases.update_linea_entrada(linea_id, linea_entrada_data, linea_num)
        return success_response(
            data=LineasEntradaResponse.model_validate(updated_data).model_dump(mode="json"),
            message="Producción linea entrada actualizada"
        )
    except NotFoundError as e:
        return error_response(
            message=str(e), status_code=status.HTTP_404_NOT_FOUND
        )
    except RepositoryError as e:
        return error_response(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/{linea_num}/{linea_id}", status_code=status.HTTP_200_OK)
def remove_linea_entrada(
        linea_id: int,
        linea_num: int,
        use_cases: LineasEntradaUseCase = Depends(get_lineas_entrada_use_case),
):
    try:
        use_cases.remove_linea_entrada(linea_id, linea_num)
        return success_response(
            data={"id_linea_entrada_removida": linea_id},
            message="Linea Entrada removida"
        )
    except RepositoryError as e:
        return error_response(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.patch("/{linea_num}/{linea_id}/update_cod_parrilla", response_model=LineasEntradaResponse,
              status_code=status.HTTP_200_OK)
def update_codigo_parrilla(
        linea_id: int,
        linea_num: int,
        data: UpdateCodigoParrillaRequest,
        use_case: LineasEntradaUseCase = Depends(get_lineas_entrada_use_case)
):
    try:
        updated_data = use_case.update_codigo_parrilla(linea_id, linea_num, data.valor)
        return success_response(
            data=LineasEntradaResponse.model_validate(updated_data).model_dump(mode="json"),
            message="Código parrilla actualizado correctamente"
        )
    except NotFoundError as e:
        return error_response(
            message=str(e), status_code=status.HTTP_404_NOT_FOUND
        )
    except RepositoryError as e:
        return error_response(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
