import logging
from typing import Dict, Any

from fastapi import APIRouter, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from src.modules.administracion_service.src.application.use_case.control_lote_asiglinea_use_case import \
    ControlLoteAsiglineaUseCase
from src.modules.administracion_service.src.infrastructure.api.schemas.control_lote_asiglinea import \
    ControlLoteAsiglineaPagination, ControlLoteAsiglineaResponse, ControlLoteAsiglineaUpdate
from src.modules.administracion_service.src.infrastructure.db.repositories.control_lote_asiglinea_repository import \
    ControlLoteAsiglineaRepository
from src.modules.administracion_service.src.infrastructure.db.repositories.tipo_limpieza_repository import \
    TipoLimpiezaRepository
from src.modules.auth_service.src.application.use_cases.audit_use_case import AuditUseCase
from src.shared.base import get_db
from src.shared.common.auditoria import get_audit_use_case
from src.shared.common.responses import success_response, error_response
from src.shared.exceptions import RepositoryError
from src.shared.security import get_current_user_data

router = APIRouter()


def get_control_lote_asiglinea_use_case(
        db: Session = Depends(get_db),
        audit_uc: AuditUseCase = Depends(get_audit_use_case)
) -> ControlLoteAsiglineaUseCase:
    return ControlLoteAsiglineaUseCase(
        control_lote_asiglinea_repository=ControlLoteAsiglineaRepository(db),
        tipo_limpieza_repository=TipoLimpiezaRepository(db),
        audit_use_case=audit_uc
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
        use_case: ControlLoteAsiglineaUseCase = Depends(get_control_lote_asiglinea_use_case),
        user_data: Dict[str, Any] = Depends(get_current_user_data)
):
    response = use_case.update_lote_asiglinea(data, lote_id, user_data)
    return success_response(
        data=response,
        message="Lote actualizado"
    )


@router.delete("/{lote_id}", status_code=status.HTTP_200_OK)
def remove_lote(
        lote_id: int,
        use_case: ControlLoteAsiglineaUseCase = Depends(get_control_lote_asiglinea_use_case),
        user_data: Dict[str, Any] = Depends(get_current_user_data)
):
    try:
        use_case.remove_lote(lote_id, user_data)
        return success_response(
            data=f"lote con id {lote_id} eliminado",
            message="Lote eliminado correctamente"
        )
    except RepositoryError as e:
        return error_response(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
