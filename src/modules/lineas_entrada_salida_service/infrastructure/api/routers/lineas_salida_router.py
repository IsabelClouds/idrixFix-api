from typing import Dict, Any, List

from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.orm import Session

from src.modules.auth_service.src.application.use_cases.audit_use_case import AuditUseCase
from src.modules.lineas_entrada_salida_service.application.use_cases.lineas_salida_use_case import LineasSalidaUseCase
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.lineas_salida import TaraIdRequest, PanzaRequest
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.lineas_shared import LineasPagination, \
    UpdateCodigoParrillaRequest, LineasFilters
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.lineas_salida import LineasSalidaResponse, \
    LineasSalidaUpdate
from src.modules.lineas_entrada_salida_service.infrastructure.db.repositories.control_tara import ControlTaraRepository
from src.modules.lineas_entrada_salida_service.infrastructure.db.repositories.lineas_salida_repository import \
    LineasSalidaRepository
from src.shared.base import get_db, get_auth_db
from src.shared.common.auditoria import get_audit_use_case
from src.shared.common.responses import success_response, error_response
from src.shared.exceptions import RepositoryError, NotFoundError
from src.shared.security import get_current_user_data

router = APIRouter()


def get_lineas_salida_use_case(
        db_externa: Session = Depends(get_db),
        db_auth: Session = Depends(get_auth_db),
        audit_uc: AuditUseCase = Depends(get_audit_use_case)
) -> LineasSalidaUseCase:
    return LineasSalidaUseCase(
        lineas_salida_repository=LineasSalidaRepository(db_externa),
        control_tara_repository=ControlTaraRepository(db_auth),
        audit_use_case=audit_uc
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
def update_linea_salida(
        linea_id: int,
        linea_salida_data: LineasSalidaUpdate,
        use_cases: LineasSalidaUseCase = Depends(get_lineas_salida_use_case),
        linea_num: int = Path(..., ge=1, le=6, description="Número de Línea (1 al 6)"),
        user_data: Dict[str, Any] = Depends(get_current_user_data)
):
    try:
        updated_data = use_cases.update_linea_salida(linea_id, linea_salida_data, linea_num, user_data)
        return success_response(
            data=LineasSalidaResponse.model_validate(updated_data).model_dump(mode="json"),
            message="Producción linea salida actualizada"
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
        user_data: Dict[str, Any] = Depends(get_current_user_data)
):
    try:
        use_cases.remove_linea_salida(linea_id, linea_num, user_data)
        return success_response(
            data={"id_linea_salida_removida": linea_id},
            message="Linea Salida removida"
        )
    except RepositoryError as e:
        return error_response(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.patch("/{linea_num}/{linea_id}/agregar_tara", response_model=LineasSalidaResponse,
              status_code=status.HTTP_200_OK)
def agregar_tara(
        linea_id: int,
        linea_num: int,
        data: TaraIdRequest,
        use_case: LineasSalidaUseCase = Depends(get_lineas_salida_use_case),
        user_data: Dict[str, Any] = Depends(get_current_user_data)
):
    try:
        updated_data = use_case.agregar_tara(linea_id, linea_num, data.tara_id, user_data)
        return success_response(
            data=LineasSalidaResponse.model_validate(updated_data).model_dump(mode="json"),
            message="Tara agregada correctamente"
        )
    except NotFoundError as e:
        return error_response(
            message=str(e), status_code=status.HTTP_404_NOT_FOUND
        )
    except RepositoryError as e:
        return error_response(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.patch("/{linea_num}/{linea_id}/update_cod_parrilla", response_model=LineasSalidaResponse,
              status_code=status.HTTP_200_OK)
def update_codigo_parrilla(
        linea_id: int,
        linea_num: int,
        data: UpdateCodigoParrillaRequest,
        use_case: LineasSalidaUseCase = Depends(get_lineas_salida_use_case),
        user_data: Dict[str, Any] = Depends(get_current_user_data)
):
    try:
        updated_data = use_case.update_codigo_parrilla(linea_id, linea_num, data.valor, user_data)
        return success_response(
            data=LineasSalidaResponse.model_validate(updated_data).model_dump(mode="json"),
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

@router.post("/{linea_num}/total", status_code=status.HTTP_200_OK)
def get_total_lineas_salida_by_filters(
        linea_num: int,
        filters: LineasFilters,
        use_case: LineasSalidaUseCase = Depends(get_lineas_salida_use_case)
):
    try:
        total_records = use_case.count_lineas_salida(filters, linea_num)
        return success_response(
            data=total_records,
            message=f"Total de produccion de la linea ${linea_num} salida obtenida correctamente"
        )
    except RepositoryError as e:
        return error_response(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.put("/{linea_num}/agregar_panza", status_code=status.HTTP_200_OK)
def agregar_panza(
        linea_num: int,
        data: PanzaRequest,
        use_case: LineasSalidaUseCase = Depends(get_lineas_salida_use_case),
        user_data: Dict[str, Any] = Depends(get_current_user_data)
):
    updated_items = use_case.agregar_panza(
        linea_num=linea_num,
        data=data,
        user_data=user_data
    )
    return success_response(
        data=f"Se actualizaron {updated_items} registros",
        message="Panza agregada correctamente a los registros"
    )
