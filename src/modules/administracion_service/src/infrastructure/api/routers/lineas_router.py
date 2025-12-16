from typing import Dict, Any

from fastapi import APIRouter, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from src.modules.administracion_service.src.application.use_case.linea_use_case import LineaUseCase
from src.modules.administracion_service.src.infrastructure.api.schemas.linea import LineaResponse, LineaCreate, \
    LineaUpdate
from src.modules.administracion_service.src.infrastructure.db.repositories.linea_repository import LineaRepository
from src.modules.administracion_service.src.infrastructure.db.repositories.planta_repository import PlantaRepository
from src.modules.auth_service.src.application.use_cases.audit_use_case import AuditUseCase
from src.shared.base import get_db
from src.shared.common.auditoria import get_audit_use_case
from src.shared.common.responses import success_response
from src.shared.security import get_current_user_data

router = APIRouter()


def get_lineas_use_case(
        db: Session = Depends(get_db),
        audit_uc: AuditUseCase = Depends(get_audit_use_case)
) -> LineaUseCase:
    return LineaUseCase(
        lineas_repository=LineaRepository(db),
        planta_repository=PlantaRepository(db),
        audit_use_case=audit_uc
    )

@router.get("/", status_code=status.HTTP_200_OK, response_model=LineaResponse)
def get_all_lineas(
        use_case: LineaUseCase = Depends(get_lineas_use_case)
):
    lineas = use_case.get_all_lineas()
    return success_response(
        data=[LineaResponse.model_validate(l).model_dump(mode="json") for l in lineas],
        message="Lineas encontradas"
    )

@router.get("/{linea_id}", status_code=status.HTTP_200_OK, response_model=LineaResponse)
def get_linea_by_id(
        linea_id: int,
        use_case: LineaUseCase = Depends(get_lineas_use_case)
):
    linea = use_case.get_linea_by_id(linea_id)
    return success_response(
        data=LineaResponse.model_validate(linea).model_dump(mode="json"),
        message="Linea encontrada"
    )

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=LineaResponse)
def create_linea(
        data: LineaCreate,
        use_case: LineaUseCase = Depends(get_lineas_use_case),
        user_data: Dict[str, Any] = Depends(get_current_user_data)
):
    new_linea = use_case.create_linea(data, user_data)
    return success_response(
        data=LineaResponse.model_validate(new_linea).model_dump(mode="json"),
        message="Linea creada"
    )

@router.patch("/{linea_id}", status_code=status.HTTP_200_OK, response_model=LineaResponse)
def update_linea(
        linea_id: int,
        data: LineaUpdate,
        use_case: LineaUseCase = Depends(get_lineas_use_case),
        user_data: Dict[str, Any] = Depends(get_current_user_data)
):
    response = use_case.update_linea(data, linea_id, user_data)
    return success_response(
        data=LineaResponse.model_validate(response).model_dump(mode="json"),
        message="Linea actualizada"
    )

@router.delete("/{linea_id}", status_code=status.HTTP_200_OK)
def soft_delete_linea(
        linea_id: int,
        use_case: LineaUseCase = Depends(get_lineas_use_case),
        user_data: Dict[str, Any] = Depends(get_current_user_data)
):
    use_case.soft_delete_linea(linea_id, user_data)
    return success_response(
        data=f"Linea eliminada {linea_id}",
        message="Linea eliminada correctamente"
    )


