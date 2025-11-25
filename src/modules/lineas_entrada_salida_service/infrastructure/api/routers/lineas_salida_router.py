from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.orm import Session

from src.modules.lineas_entrada_salida_service.application.use_cases.lineas_salida_use_case import LineasSalidaUseCase
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.lineas_salida import TaraIdRequest
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.lineas_filters import LineasPagination
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.lineas_salida import LineasSalidaResponse, \
    LineasSalidaUpdate
from src.modules.lineas_entrada_salida_service.infrastructure.db.repositories.control_tara import ControlTaraRepository
from src.modules.lineas_entrada_salida_service.infrastructure.db.repositories.lineas_salida_repository import \
    LineasSalidaRepository
from src.shared.base import get_db, get_auth_db
from src.shared.common.responses import success_response, error_response
from src.shared.exceptions import RepositoryError, NotFoundError

router = APIRouter()


def get_lineas_salida_use_case(
        db_externa: Session = Depends(get_db),
        db_auth: Session = Depends(get_auth_db)
) -> LineasSalidaUseCase:
    return LineasSalidaUseCase(
        lineas_salida_repository=LineasSalidaRepository(db_externa),
        control_tara_repository=ControlTaraRepository(db_auth)
    )


@router.post("/{linea_num}/paginated", status_code=status.HTTP_200_OK)
def get_all_lineas_salida(
        pagination_params: LineasPagination,
        linea_num: int = Path(..., ge=1, le=6, description="Número de Línea (1 al 6)"),
        use_case: LineasSalidaUseCase = Depends(get_lineas_salida_use_case)
):
    try:
        pagination_result = use_case.get_lineas_salida_paginated_by_filters(
            filters=pagination_params,
            linea_num=linea_num
        )

        response_data = [
            LineasSalidaResponse.model_validate(d).model_dump(mode="json")
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
            message=f"Producción de Linea Salida {linea_num} obtenidas",
        )

    except RepositoryError as e:
        return error_response(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{linea_num}/{linea_id}", response_model=LineasSalidaResponse, status_code=status.HTTP_200_OK)
def get_linea_salida_by_id(
        linea_id: int,
        use_cases: LineasSalidaUseCase = Depends(get_lineas_salida_use_case),
        linea_num: int = Path(..., ge=1, le=6, description="Número de Línea (1 al 6)"),

):
    data = use_cases.get_linea_salida_by_id(linea_id, linea_num)
    if not data:
        return error_response(
            message="Producción linea salida no encontrada", status_code=status.HTTP_404_NOT_FOUND
        )
    return success_response(
        data=LineasSalidaResponse.model_validate(data).model_dump(mode="json"),
        message="Producción linea salida obtenida",
    )

@router.patch("/{linea_num}/{linea_id}", response_model=LineasSalidaResponse, status_code=status.HTTP_200_OK)
def update_linea_entrada(
        linea_id: int,
        linea_salida_data: LineasSalidaUpdate,
        use_cases: LineasSalidaUseCase = Depends(get_lineas_salida_use_case),
        linea_num: int = Path(..., ge=1, le=6, description="Número de Línea (1 al 6)")
):
    try:
        updated_data = use_cases.update_linea_salida(linea_id, linea_salida_data, linea_num)
        return success_response(
            data=LineasSalidaResponse.model_validate(updated_data).model_dump(mode="json"),
            message = "Producción linea salida actualizada"
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
def remove_linea_salida(
        linea_id: int,
        linea_num: int,
        use_cases: LineasSalidaUseCase = Depends(get_lineas_salida_use_case),
):
    try:
        use_cases.remove_linea_salida(linea_id,linea_num)
        return success_response(
            data={"id_linea_salida_removida": linea_id},
            message="Linea Salida removida"
        )
    except RepositoryError as e:
        return error_response(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.patch("/{linea_num}/{linea_id}/agregar_tara", response_model=LineasSalidaResponse, status_code=status.HTTP_200_OK)
def agregar_tara(
        linea_id: int,
        linea_num: int,
        data: TaraIdRequest,
        use_case: LineasSalidaUseCase = Depends(get_lineas_salida_use_case)
):
    try:
        updated_data = use_case.agregar_tara(linea_id, linea_num, data.tara_id)
        return success_response(
            data=LineasSalidaResponse.model_validate(updated_data).model_dump(mode="json"),
            message= "Tara agregada correctamente"
        )
    except NotFoundError as e:
        return error_response(
            message=str(e), status_code=status.HTTP_404_NOT_FOUND
        )
    except RepositoryError as e:
        return error_response(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
