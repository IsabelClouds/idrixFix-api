import logging
from typing import Dict, Any

from fastapi import APIRouter, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from src.modules.auth_service.src.application.use_cases.audit_use_case import AuditUseCase
from src.modules.lineas_entrada_salida_service.application.use_cases.control_tara_use_case import ControlTaraUseCase
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.control_tara import TaraResponse, TaraCreate
from src.modules.lineas_entrada_salida_service.infrastructure.db.repositories.control_tara import ControlTaraRepository
from src.shared.base import get_auth_db
from src.shared.common.auditoria import get_audit_use_case
from src.shared.common.responses import success_response, error_response
from src.shared.security import get_current_user_data

router = APIRouter()


def get_tara_use_case(db: Session = Depends(get_auth_db),
                      audit_uc: AuditUseCase = Depends(get_audit_use_case)) -> ControlTaraUseCase:
    return ControlTaraUseCase(
        control_tara_repository=ControlTaraRepository(db),
        audit_use_case=audit_uc
    )


@router.get("/", status_code=status.HTTP_200_OK)
def get_all_taras(
        use_case: ControlTaraUseCase = Depends(get_tara_use_case)
):
    return success_response(
        data=use_case.get_all_taras(),
        message="Taras obtenidas"
    )


@router.post("/", response_model=TaraResponse, status_code=status.HTTP_201_CREATED)
def create_tara(
        tara_data: TaraCreate,
        control_tara_use_case: ControlTaraUseCase = Depends(get_tara_use_case),
        user_data: Dict[str, Any] = Depends(get_current_user_data)
):
    new_data = control_tara_use_case.create_tara(tara_data, user_data)
    return success_response(
        data=TaraResponse.model_validate(new_data).model_dump(mode="json"),
        message="Tara creada",
        status_code=201
    )


@router.get("/{tara_id}", response_model=TaraResponse, status_code=status.HTTP_200_OK)
def get_tara_by_id(
        tara_id: int,
        use_case: ControlTaraUseCase = Depends(get_tara_use_case)
):
    data = use_case.get_tara_by_id(tara_id)
    if not data:
        return error_response(
            message="Tara no encontrada", status_code=status.HTTP_404_NOT_FOUND
        )
    return success_response(
        data=TaraResponse.model_validate(data).model_dump(mode="json"),
        message="Tara obtenida"
    )


@router.delete("/{tara_id}", status_code=status.HTTP_200_OK)
def soft_delete_tara(
        tara_id: int,
        use_case: ControlTaraUseCase = Depends(get_tara_use_case),
        user_data: Dict[str, Any] = Depends(get_current_user_data)
):
    return success_response(
        data=use_case.soft_delete(tara_id, user_data),
        message=f"Tara con id {tara_id} eliminada con exito"
    )
