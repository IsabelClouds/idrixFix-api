from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.modules.administracion_service.src.application.use_case.tipo_limpieza_use_case import TipoLimpiezaUseCase
from src.modules.administracion_service.src.infrastructure.api.schemas.tipo_limpieza import TipoLimpiezaResponse
from src.modules.administracion_service.src.infrastructure.db.repositories.tipo_limpieza_repository import \
    TipoLimpiezaRepository
from src.shared.base import get_db
from src.shared.common.responses import success_response

router = APIRouter()

def get_tipo_limpieza_use_case(
        db: Session = Depends(get_db)
) -> TipoLimpiezaUseCase:
    return TipoLimpiezaUseCase(
        tipo_limpieza_repository=TipoLimpiezaRepository(db)
    )

@router.get("/", response_model=TipoLimpiezaResponse, status_code=status.HTTP_200_OK)
def get_all_plantas(
        use_case: TipoLimpiezaUseCase = Depends(get_tipo_limpieza_use_case)
):
    tipos_limpieza = use_case.get_all_tipo_limpieza()
    return success_response(
        data=[TipoLimpiezaResponse.model_validate(tp).model_dump(mode="json") for tp in tipos_limpieza],
        message="Tipos de Limpieza obtenidas"
    )