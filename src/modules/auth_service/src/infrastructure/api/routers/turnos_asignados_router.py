from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

# Dependencias de BD
from src.shared.base import get_auth_db, get_db

# Respuestas y seguridad
from src.shared.common.responses import success_response
from src.shared.security import get_current_user_data

# Repositorios (Usuario es necesario para los casos de uso)
from src.modules.auth_service.src.infrastructure.db.repositories.usuario_repository import UsuarioRepository
from src.modules.auth_service.src.infrastructure.db.repositories.turno_asignado_repository import TurnoAsignadoRepository
from src.modules.auth_service.src.infrastructure.db.repositories.turno_externo_repository import TurnoExternaRepository

# Casos de uso (Turnos y Auditoría)
from src.modules.auth_service.src.application.use_cases.turno_asignado_use_case import TurnoAsignadoUseCase
from src.modules.auth_service.src.application.use_cases.turno_externo_use_case import TurnoExternaUseCase
from src.shared.common.auditoria import get_audit_use_case
from src.modules.auth_service.src.application.use_cases.audit_use_case import AuditUseCase

# Schemas
from src.modules.auth_service.src.infrastructure.api.schemas.usuarios import (
    TurnoAsignadoCreate, 
    TurnoAsignadoResponse, 
    TurnoExternoResponse
)

router = APIRouter(
    prefix="/usuarios/{id_usuario}/turnos",
    tags=["Asignación de Turnos"]
)

# Dependencia para el caso de uso de asignación de turnos
def get_turno_asignado_use_case(
    db_auth: Session = Depends(get_auth_db),
    db_externa: Session = Depends(get_db),
    audit_uc: AuditUseCase = Depends(get_audit_use_case)
) -> TurnoAsignadoUseCase:
    """Dependency para obtener el caso de uso de asignación de turnos"""
    return TurnoAsignadoUseCase(
        usuario_repository=UsuarioRepository(db_auth),
        turno_asignado_repository=TurnoAsignadoRepository(db_auth),
        turno_externa_repository=TurnoExternaRepository(db_externa),
        audit_use_case=audit_uc
    )

# Dependencia para el caso de uso de turnos externos (la lista maestra)
def get_turno_externo_use_case(
    db_externa: Session = Depends(get_db) # <-- Inyecta la DB externa
) -> TurnoExternaUseCase:
    """Dependency para obtener el caso de uso de turnos externos"""
    return TurnoExternaUseCase(
        turno_externa_repository=TurnoExternaRepository(db_externa)
    )


@router.get("/", response_model=List[TurnoAsignadoResponse], status_code=status.HTTP_200_OK)
def get_turnos_de_usuario(
    id_usuario: int,
    use_case: TurnoAsignadoUseCase = Depends(get_turno_asignado_use_case)
):
    """Obtiene los turnos asignados a un usuario específico"""
    data = use_case.get_turnos_por_usuario(id_usuario)
    return success_response(
        data=[TurnoAsignadoResponse.model_validate(d).model_dump() for d in data],
        message="Turnos obtenidos"
    )

@router.post("/", response_model=TurnoAsignadoResponse, status_code=status.HTTP_201_CREATED)
def asignar_turno_a_usuario(
    id_usuario: int,
    turno_data: TurnoAsignadoCreate,
    use_case: TurnoAsignadoUseCase = Depends(get_turno_asignado_use_case),
    user_data: Dict[str, Any] = Depends(get_current_user_data)
):
    """Asigna un turno de trabajo externo a un usuario"""
    new_data = use_case.asignar_turno(id_usuario, turno_data.id_turno_externo, user_data)
    return success_response(
        data=TurnoAsignadoResponse.model_validate(new_data).model_dump(),
        message="Turno asignado",
        status_code=201
    )

@router.delete("/{id_turno_externo}", status_code=status.HTTP_200_OK)
def remover_turno_de_usuario(
    id_usuario: int,
    id_turno_externo: int,
    use_case: TurnoAsignadoUseCase = Depends(get_turno_asignado_use_case),
    user_data: Dict[str, Any] = Depends(get_current_user_data)
):
    """Remueve la asignación de un turno de un usuario"""
    use_case.remover_turno(id_usuario, id_turno_externo, user_data)
    return success_response(
        data={"id_usuario": id_usuario, "id_turno_externo_removido": id_turno_externo},
        message="Asignación de turno removida"
    )

@router.get(
    "/turnos/", 
    response_model=List[TurnoExternoResponse], 
    status_code=status.HTTP_200_OK
)
def get_all_active_turnos(
    use_case: TurnoExternaUseCase = Depends(get_turno_externo_use_case)
):
    """
    Obtiene una lista de todos los turnos de trabajo externos
    que se encuentran activos.
    """
    # El caso de uso devuelve entidades de dominio
    turnos_entities = use_case.get_all_active_turnos()
    
    # Mapeamos las entidades a los Schemas de Respuesta Pydantic
    response_data = [
        TurnoExternoResponse.model_validate(turno).model_dump() 
        for turno in turnos_entities
    ]
    
    return success_response(
        data=response_data,
        message="Turnos activos obtenidos"
    )