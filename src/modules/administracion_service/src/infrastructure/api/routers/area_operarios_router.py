from fastapi import APIRouter, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from src.modules.administracion_service.src.application.use_case.area_operarios_use_case import AreaOperariosUseCase
from src.modules.administracion_service.src.infrastructure.api.schemas.area_operarios import AreaOperariosRequest, \
    AreaOperariosResponse
from src.modules.administracion_service.src.infrastructure.db.repositories.area_operarios_repository import \
    AreaOperariosRepository
from src.shared.base import get_db
from src.shared.common.responses import success_response

router = APIRouter()

def get_area_operarios_use_case(
        db: Session = Depends(get_db)
) -> AreaOperariosUseCase:
    return AreaOperariosUseCase(
        area_operarios_repository=AreaOperariosRepository(db)
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

@router.post("/", status_code=status.HTTP_200_OK, response_model=AreaOperariosResponse)
def create_area_operario(
        data: AreaOperariosRequest,
        use_case: AreaOperariosUseCase = Depends(get_area_operarios_use_case)
):
    new_data = use_case.create_area_operarios(data)
    return success_response(
        data=AreaOperariosResponse.model_validate(new_data).model_dump(mode="json"),
        message="Area Operarios creada satisfactoriamente",
        status_code=201
    )

@router.patch("/{area_id}", status_code=status.HTTP_200_OK, response_model=AreaOperariosResponse)
def update_area_operario(
        area_id: int,
        data: AreaOperariosRequest,
        use_case: AreaOperariosUseCase = Depends(get_area_operarios_use_case)
):
    response = use_case.update_area_operarios(data, area_id)

    return success_response(
        data=AreaOperariosResponse.model_validate(response).model_dump(mode="json"),
        message="Area actualizada satisfactoriamente"
    )
