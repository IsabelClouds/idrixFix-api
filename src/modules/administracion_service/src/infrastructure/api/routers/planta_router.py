from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from src.modules.administracion_service.src.application.use_case.planta_use_case import PlantaUseCase
from src.modules.administracion_service.src.infrastructure.api.schemas.planta import PlantaResponse
from src.modules.administracion_service.src.infrastructure.db.repositories import planta_repository
from src.modules.administracion_service.src.infrastructure.db.repositories.planta_repository import PlantaRepository
from src.shared.base import get_db
from src.shared.common.responses import success_response

router = APIRouter()

def get_planta_use_case(
        db: Session = Depends(get_db)
) -> PlantaUseCase:
    return PlantaUseCase(
        planta_repository=PlantaRepository(db)
    )

@router.get("/", status_code=status.HTTP_200_OK)
def get_all_plantas(
        use_case: PlantaUseCase = Depends(get_planta_use_case)
):
    plantas = use_case.get_all_plantas()
    return success_response(
        data=[PlantaResponse.model_validate(p).model_dump(mode="json") for p in plantas],
        message="Plantas obtenidas"
    )
