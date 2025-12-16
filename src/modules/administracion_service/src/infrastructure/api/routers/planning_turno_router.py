from typing import Dict, Any

from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from src.modules.administracion_service.src.application.use_case.planning_turno_use_case import PlanningTurnoUseCase
from src.modules.administracion_service.src.infrastructure.api.schemas.planning_turno import (
    PlanningTurnoPagination, PlanningTurnoResponse, PlanningTurnoUpdate
)
from src.modules.administracion_service.src.infrastructure.db.repositories.planning_turno_repository import (
    PlanningTurnoRepository
)
from src.modules.auth_service.src.application.use_cases.audit_use_case import AuditUseCase
from src.shared.base import get_db
from src.shared.common.auditoria import get_audit_use_case
from src.shared.common.responses import success_response, error_response
from src.shared.exceptions import RepositoryError
from src.shared.security import get_current_user_data

router = APIRouter()


def get_use_case(
        db: Session = Depends(get_db),
        audit_uc: AuditUseCase = Depends(get_audit_use_case)
) -> PlanningTurnoUseCase:
    return PlanningTurnoUseCase(
        planning_turno_repository=PlanningTurnoRepository(db),
        audit_use_case=audit_uc
    )


@router.get("/{id}", response_model=PlanningTurnoResponse)
def get_by_id(id: int, use_case: PlanningTurnoUseCase = Depends(get_use_case)):
    try:
        record = use_case.get_by_id(id)
        return success_response(data=record, message="Registro obtenido")
    except RepositoryError as e:
        return error_response(message=str(e), status_code=500)


@router.post("/paginated")
def get_paginated(
        pagination: PlanningTurnoPagination,
        use_case: PlanningTurnoUseCase = Depends(get_use_case)
):
    try:
        pagination_result = use_case.get_paginated_by_filters(pagination)

        response_data = [
            PlanningTurnoResponse.model_validate(d).model_dump(mode="json")
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
            message="Registros obtenidos"
        )
    except RepositoryError as e:
        return error_response(message=str(e), status_code=500)


@router.patch("/{id}", response_model=PlanningTurnoResponse)
def update(
        id: int, data: PlanningTurnoUpdate,
        use_case: PlanningTurnoUseCase = Depends(get_use_case),
        user_data: Dict[str, Any] = Depends(get_current_user_data)
):
    planning_turno = use_case.update(id, data, user_data)
    return success_response(
        data=planning_turno,
        message="Registro actualizado"
    )


@router.delete("/{id}")
def delete(
        id: int,
        use_case: PlanningTurnoUseCase = Depends(get_use_case),
        user_data: Dict[str, Any] = Depends(get_current_user_data)
):
    use_case.remove(id, user_data)
    return success_response(
        data=f"Registro {id} eliminado",
        message="Registro eliminado"
    )
