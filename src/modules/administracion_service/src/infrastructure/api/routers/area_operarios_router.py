from typing import Dict, Any

from fastapi import APIRouter, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from src.modules.administracion_service.src.application.use_case.area_operarios_use_case import AreaOperariosUseCase
from src.modules.administracion_service.src.infrastructure.api.schemas.area_operarios import AreaOperariosRequest, \
    AreaOperariosResponse
from src.modules.administracion_service.src.infrastructure.db.repositories.area_operarios_repository import \
    AreaOperariosRepository
from src.modules.auth_service.src.application.use_cases.audit_use_case import AuditUseCase
from src.shared.base import get_db
from src.shared.common.auditoria import get_audit_use_case
from src.shared.common.responses import success_response, error_response
from src.shared.exceptions import RepositoryError
from src.shared.security import get_current_user_data

router = APIRouter()

def get_area_operarios_use_case(
        db: Session = Depends(get_db),
        audit_uc: AuditUseCase = Depends(get_audit_use_case)
) -> AreaOperariosUseCase:
    return AreaOperariosUseCase(
        area_operarios_repository=AreaOperariosRepository(db),
        audit_use_case=audit_uc
    )

@router.get("/", status_code=status.HTTP_200_OK)
def get_all_area_operarios(
        use_case: AreaOperariosUseCase = Depends(get_area_operarios_use_case)
):
    response = use_case.get_all_areas_operarios()
    return success_response(
        data=response,
        message="Areas Operarios Obtenidas"
    )

@router.get("/{area_id}", status_code=status.HTTP_200_OK, response_model=AreaOperariosResponse)
def get_area_operario_by_id(
        area_id: int,
        use_case: AreaOperariosUseCase = Depends(get_area_operarios_use_case)
):
    response = use_case.get_area_by_id(area_id)
    return success_response(
        data=AreaOperariosResponse.model_validate(response).model_dump(mode="json"),
        message="Area Operarios Obtenidas"
    )

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=AreaOperariosResponse)
def create_area_operario(
        data: AreaOperariosRequest,
        use_case: AreaOperariosUseCase = Depends(get_area_operarios_use_case),
        user_data: Dict[str, Any] = Depends(get_current_user_data)
):
    new_data = use_case.create_area_operarios(data, user_data)
    return success_response(
        data=AreaOperariosResponse.model_validate(new_data).model_dump(mode="json"),
        message="Area Operarios creada satisfactoriamente",
        status_code=201
    )

@router.patch("/{area_id}", status_code=status.HTTP_200_OK, response_model=AreaOperariosResponse)
def update_area_operario(
        area_id: int,
        data: AreaOperariosRequest,
        use_case: AreaOperariosUseCase = Depends(get_area_operarios_use_case),
        user_data: Dict[str, Any] = Depends(get_current_user_data)
):
    response = use_case.update_area_operarios(data, area_id, user_data)

    return success_response(
        data=AreaOperariosResponse.model_validate(response).model_dump(mode="json"),
        message="Area actualizada satisfactoriamente"
    )

@router.delete("/{area_id}", status_code=status.HTTP_200_OK)
def remove_area(
        area_id: int,
        use_case: AreaOperariosUseCase = Depends(get_area_operarios_use_case),
        user_data: Dict[str, Any] = Depends(get_current_user_data)
):
    try:
        use_case.remove_area(area_id, user_data)
        return success_response(
            data={"id_area removida": area_id},
            message="Area Operarios removida"
        )
    except RepositoryError as e:
        return error_response(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
