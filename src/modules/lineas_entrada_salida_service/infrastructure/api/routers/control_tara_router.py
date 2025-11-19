import logging

from fastapi import APIRouter, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from src.modules.lineas_entrada_salida_service.application.use_cases.control_tara_use_case import ControlTaraUseCase
from src.modules.lineas_entrada_salida_service.infrastructure.api.schemas.control_tara import TaraResponse, TaraCreate
from src.modules.lineas_entrada_salida_service.infrastructure.db.repositories.control_tara import ControlTaraRepository
from src.shared.base import get_auth_db
from src.shared.common.responses import success_response, error_response

router = APIRouter()

def get_tara_use_case(db: Session = Depends(get_auth_db)) -> ControlTaraUseCase:
    return ControlTaraUseCase(
        control_tara_repository=ControlTaraRepository(db)
    )

@router.post("/", response_model=TaraResponse, status_code=status.HTTP_201_CREATED)
def create_tara(
        tara_data: TaraCreate,
        control_tara_use_case: ControlTaraUseCase = Depends(get_tara_use_case),
):
    new_data = control_tara_use_case.create_tara(tara_data)
    return success_response(
        data=TaraResponse.model_validate(new_data).model_dump(mode="json"),
        message="Tara creada",
        status_code=201
    )

#TODO fix
# @router.get("/{tara_id}", response_model=TaraResponse, status_code=status.HTTP_201_CREATED)
# def get_tara_by_id(
#         tara_id: int,
#         use_case: ControlTaraUseCase = Depends(get_tara_use_case)
# ):
#     data = use_case.get_tara_by_id(tara_id)
#     if not data:
#         return error_response(
#             message="Tara no encontrada", status_code=status.HTTP_404_NOT_FOUND
#         )
#     return success_response(
#         data=TaraResponse.model_validate(data).model_dump(mode="json"),
#         message="Tara obtenida",
#     )
