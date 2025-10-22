from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from src.shared.base import get_auth_db, get_db
# Necesitarás una dependencia similar para tu DB externa
from src.shared.common.responses import success_response
from src.modules.auth_service.src.infrastructure.db.repositories.usuario_repository import UsuarioRepository
from src.modules.auth_service.src.infrastructure.db.repositories.linea_asignada_repository import LineaAsignadaRepository
# Repo externo
from src.modules.auth_service.src.infrastructure.db.repositories.linea_externa_repository import LineaExternaRepository
from src.modules.auth_service.src.application.use_cases.linea_asignada_use_case import LineaAsignadaUseCase
from src.modules.auth_service.src.application.use_cases.linea_externa_use_case import LineaExternaUseCase
from src.modules.auth_service.src.infrastructure.api.schemas.usuarios import LineaAsignadaCreate, LineaAsignadaResponse, LineaExternaResponse

router = APIRouter(
    prefix="/usuarios/{id_usuario}/lineas",
    tags=["Asignación de Líneas"]
)

def get_linea_asignada_use_case(
    db_auth: Session = Depends(get_auth_db),
    db_externa: Session = Depends(get_db)
) -> LineaAsignadaUseCase:
    """Dependency para obtener el caso de uso de asignación de líneas"""
    return LineaAsignadaUseCase(
        usuario_repository=UsuarioRepository(db_auth),
        linea_asignada_repository=LineaAsignadaRepository(db_auth),
        linea_externa_repository=LineaExternaRepository(db_externa)
    )


@router.get("/", response_model=List[LineaAsignadaResponse], status_code=status.HTTP_200_OK)
def get_lineas_de_usuario(
    id_usuario: int,
    use_case: LineaAsignadaUseCase = Depends(get_linea_asignada_use_case)
):
    """Obtiene las líneas asignadas a un usuario específico"""
    data = use_case.get_lineas_por_usuario(id_usuario)
    return success_response(
        data=[LineaAsignadaResponse.model_validate(d).model_dump() for d in data],
        message="Líneas obtenidas"
    )

@router.post("/", response_model=LineaAsignadaResponse, status_code=status.HTTP_201_CREATED)
def asignar_linea_a_usuario(
    id_usuario: int,
    linea_data: LineaAsignadaCreate,
    use_case: LineaAsignadaUseCase = Depends(get_linea_asignada_use_case)
):
    """Asigna una línea de trabajo externa a un usuario"""
    new_data = use_case.asignar_linea(id_usuario, linea_data.id_linea_externa)
    return success_response(
        data=LineaAsignadaResponse.model_validate(new_data).model_dump(),
        message="Línea asignada",
        status_code=201
    )

@router.delete("/{id_linea_externa}", status_code=status.HTTP_200_OK)
def remover_linea_de_usuario(
    id_usuario: int,
    id_linea_externa: int,
    use_case: LineaAsignadaUseCase = Depends(get_linea_asignada_use_case)
):
    """Remueve la asignación de una línea de un usuario"""
    use_case.remover_linea(id_usuario, id_linea_externa)
    return success_response(
        data={"id_usuario": id_usuario, "id_linea_externa_removida": id_linea_externa},
        message="Asignación de línea removida"
    )

def get_linea_externa_use_case(
    db_externa: Session = Depends(get_db) # <-- Inyecta la DB externa
) -> LineaExternaUseCase:
    """Dependency para obtener el caso de uso de líneas externas"""
    return LineaExternaUseCase(
        linea_externa_repository=LineaExternaRepository(db_externa)
    )

@router.get(
    "/lineas/", 
    response_model=List[LineaExternaResponse], 
    status_code=status.HTTP_200_OK
)
def get_all_active_lines(
    use_case: LineaExternaUseCase = Depends(get_linea_externa_use_case)
):
    """
    Obtiene una lista de todas las líneas de trabajo externas
    que se encuentran activas.
    """
    # El caso de uso devuelve entidades de dominio
    lineas_entities = use_case.get_all_active_lines()
    
    # Mapeamos las entidades a los Schemas de Respuesta Pydantic
    response_data = [
        LineaExternaResponse.model_validate(linea).model_dump() 
        for linea in lineas_entities
    ]
    
    return success_response(
        data=response_data,
        message="Líneas activas obtenidas"
    )