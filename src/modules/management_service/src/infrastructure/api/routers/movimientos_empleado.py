from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from src.shared.base import get_db
from math import ceil
from src.shared.common.responses import success_response, error_response
from src.shared.exceptions import RepositoryError, NotFoundError
from src.shared.security import get_current_user_data
# Importar el repositorio y casos de uso del movimiento
from src.modules.management_service.src.infrastructure.db.repositories.movimientos_operario import (
    WorkerMovementRepository, RefMotivoRepository, RefDestinoMotivoRepository
)
from src.modules.management_service.src.application.use_cases.movimientos_operario import (
    WorkerMovementUseCases, RefMotivoUseCases, RefDestinoMotivoUseCases
)
# Importar los schemas del movimiento
from src.modules.management_service.src.infrastructure.api.schemas.movimientos_operario import (
    WorkerMovementCreate,
    WorkerMovementUpdate,
    WorkerMovementResponse,
    WorkerMovementFilters,
    WorkerMovementPagination,
    WorkerMovementPaginatedResponse,
    RefDestinoMotivoResponse,
    RefMotivoResponse,
    RefMotivoPagination,
    RefDestinoMotivoPagination,
    RefDestinoMotivoFilters,
    RefMotivoFilters
)

router = APIRouter()

# Definir la función de dependencia para los nuevos casos de uso
def get_movement_use_cases(db: Session = Depends(get_db)) -> WorkerMovementUseCases:
    repository = WorkerMovementRepository(db)
    return WorkerMovementUseCases(repository)
def get_ref_motivo_use_cases(db: Session = Depends(get_db)) -> RefMotivoUseCases:
    repository = RefMotivoRepository(db)
    return RefMotivoUseCases(repository)

def get_ref_destino_motivo_use_cases(db: Session = Depends(get_db)) -> RefDestinoMotivoUseCases:
    repository = RefDestinoMotivoRepository(db)
    return RefDestinoMotivoUseCases(repository)


@router.post("/", response_model=WorkerMovementResponse, status_code=status.HTTP_201_CREATED)
def create_movement(
    movement_data: WorkerMovementCreate,
    use_cases: WorkerMovementUseCases = Depends(get_movement_use_cases),
):
    new_data = use_cases.create_movement(movement_data)
    return success_response(
        data=WorkerMovementResponse.model_validate(new_data).model_dump(mode="json"),
        message="Movimiento creado",
        status_code=201,
    )


@router.get(
    "/{movement_id}", response_model=WorkerMovementResponse, status_code=status.HTTP_200_OK
)
def get_movement_by_id(
    movement_id: int, use_cases: WorkerMovementUseCases = Depends(get_movement_use_cases)
):
    data = use_cases.get_movement_by_id(movement_id)
    if not data:
        return error_response(
            message="Movimiento no encontrado", status_code=status.HTTP_404_NOT_FOUND
        )
    return success_response(
        data=WorkerMovementResponse.model_validate(data).model_dump(mode="json"),
        message="Movimiento obtenido",
    )

# 1. Controlador para EDITAR (PUT)
@router.put(
    "/{movement_id}", response_model=WorkerMovementResponse, status_code=status.HTTP_200_OK
)
def update_movement_controller(
    movement_id: int,
    movement_data: WorkerMovementUpdate,
    use_cases: WorkerMovementUseCases = Depends(get_movement_use_cases),
):
    try:
        updated_data = use_cases.update_movement(movement_id, movement_data)
        return success_response(
            data=WorkerMovementResponse.model_validate(updated_data).model_dump(mode="json"),
            message="Movimiento actualizado",
        )
    except NotFoundError as e:
        return error_response(
            message=str(e), status_code=status.HTTP_404_NOT_FOUND
        )
    except RepositoryError as e:
        return error_response(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# 2. Controlador para ELIMINAR (DELETE - Hard Delete)
@router.delete("/{movement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movement_controller(
    movement_id: int, use_cases: WorkerMovementUseCases = Depends(get_movement_use_cases)
):
    try:
        use_cases.delete_movement(movement_id)
        # El código 204 indica que la petición fue exitosa y no hay contenido a retornar
        return success_response(
            data=None,
            message="Movimiento eliminado permanentemente",
            status_code=status.HTTP_204_NO_CONTENT,
        )
    except NotFoundError as e:
        # Aquí puedes decidir si 404 o 500, pero 404 es común para indicar que el recurso no existe
        return error_response(
            message=str(e), status_code=status.HTTP_404_NOT_FOUND
        )
    except RepositoryError as e:
        return error_response(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# 3. Controlador para OBTENER EL TOTAL DE REGISTROS POR FILTROS (POST)
# Usamos POST para pasar los filtros en el cuerpo de la petición.
@router.post("/total", status_code=status.HTTP_200_OK)
def get_total_movements_by_filters(
    filters: WorkerMovementFilters,
    use_cases: WorkerMovementUseCases = Depends(get_movement_use_cases),
    user_data: Dict[str, Any] = Depends(get_current_user_data)
):
    try:
        allowed_lines_ids = user_data.get("lineas", [])
        total_records = use_cases.count_movements_by_filters(
            filters=filters, 
            allowed_lines=allowed_lines_ids
        )
        return success_response(
            data=total_records,
            message="Total de movimientos obtenido",
        )
    except RepositoryError as e:
        return error_response(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# 4. Controlador para OBTENER REGISTROS PAGINADOS POR FILTROS (POST)
# Usamos POST para pasar los filtros y parámetros de paginación en el cuerpo.
@router.post("/paginated", status_code=status.HTTP_200_OK)
def get_movements_paginated(
    pagination_params: WorkerMovementPagination,
    use_cases: WorkerMovementUseCases = Depends(get_movement_use_cases),
    user_data: Dict[str, Any] = Depends(get_current_user_data)
):
    try:
        allowed_lines_ids = user_data.get("lineas", [])
        pagination_result = use_cases.get_movements_paginated_by_filters(
            filters=pagination_params,
            allowed_lines=allowed_lines_ids
        )
        
        # Mapeamos las entidades de dominio ('data') a los schemas de respuesta
        response_data = [
            WorkerMovementResponse.model_validate(d).model_dump(mode="json")
            for d in pagination_result["data"]
        ]
        
        # Construimos la respuesta final, incluyendo los metadatos de paginación
        response_data_with_meta = {
            "total_records": pagination_result["total_records"],
            "total_pages": pagination_result["total_pages"],
            "page": pagination_result["page"],
            "page_size": pagination_result["page_size"],
            "data": response_data,
        }
        
        return success_response(
            data=response_data_with_meta,
            message="Movimientos paginados obtenidos",
        )
    except RepositoryError as e:
        return error_response(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
# --- ENDPOINTS: REF_MOTIVOS ---

# 1. TOTAL: Controlador para obtener el TOTAL de Motivos Activos
@router.post("/motivos/total", status_code=status.HTTP_200_OK)
def get_total_active_motives(
    filters: RefMotivoFilters,
    use_cases: RefMotivoUseCases = Depends(get_ref_motivo_use_cases),
):
    """Obtiene el número total de registros RefMotivos con estado='ACTIVO'."""
    try:
        total_records = use_cases.count_active_motives(filters)
        return success_response(
            data=total_records,
            message="Total de motivos activos obtenido",
        )
    except RepositoryError as e:
        return error_response(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# 2. PAGINATED: Controlador para obtener Motivos Activos Paginados
@router.post("/motivos/paginated", status_code=status.HTTP_200_OK)
def get_active_motives_paginated(
    pagination_params: RefMotivoPagination,
    use_cases: RefMotivoUseCases = Depends(get_ref_motivo_use_cases),
):
    """Entrega los registros activos de RefMotivos paginados."""
    try:
        # 1. Obtener la data paginada (lista de entidades)
        data_entities = use_cases.get_active_paginated_motives(pagination_params)
        
        # 2. Obtener el total (requiere una llamada separada al use case de conteo)
        total_records = use_cases.count_active_motives(pagination_params)
        
        # 3. Mapeo y Respuesta
        response_data = [
            RefMotivoResponse.model_validate(d).model_dump(mode="json")
            for d in data_entities
        ]
        
        total_pages = ceil(total_records / pagination_params.page_size) if total_records > 0 else 0

        response_data_with_meta = {
            "total_records": total_records,
            "total_pages": total_pages,
            "page": pagination_params.page,
            "page_size": pagination_params.page_size,
            "data": response_data,
        }
        
        return success_response(
            data=response_data_with_meta,
            message="Motivos activos paginados obtenidos",
        )
    except RepositoryError as e:
        return error_response(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# --- ENDPOINTS: REF_DESTINOS_MOTIVOS ---

# 3. TOTAL: Controlador para obtener el TOTAL de Destinos por Motivo
@router.post("/destinos_motivos/total", status_code=status.HTTP_200_OK)
def get_total_destinos_by_motivo(
    filters: RefDestinoMotivoFilters,
    use_cases: RefDestinoMotivoUseCases = Depends(get_ref_destino_motivo_use_cases),
):
    """Obtiene el número total de registros RefDestinosMotivos filtrados por id_motivo."""
    try:
        total_records = use_cases.count_destinations_by_motivo(filters)
        return success_response(
            data=total_records,
            message=f"Total de destinos para el motivo ID {filters.id_motivo} obtenido",
        )
    except RepositoryError as e:
        return error_response(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# 4. PAGINATED: Controlador para obtener Destinos por Motivo Paginados
@router.post("/destinos_motivos/paginated", status_code=status.HTTP_200_OK)
def get_destinos_by_motivo_paginated(
    pagination_params: RefDestinoMotivoPagination,
    use_cases: RefDestinoMotivoUseCases = Depends(get_ref_destino_motivo_use_cases),
):
    """Entrega los registros de RefDestinosMotivos filtrados por id_motivo, paginados."""
    try:
        # 1. Obtener la data paginada (lista de entidades)
        data_entities = use_cases.get_destinations_paginated_by_motivo(pagination_params)
        
        # 2. Obtener el total (requiere una llamada separada al use case de conteo)
        total_records = use_cases.count_destinations_by_motivo(pagination_params) # Reutiliza los filtros
        
        # 3. Mapeo y Respuesta
        response_data = [
            RefDestinoMotivoResponse.model_validate(d).model_dump(mode="json")
            for d in data_entities
        ]

        total_pages = ceil(total_records / pagination_params.page_size) if total_records > 0 else 0

        response_data_with_meta = {
            "total_records": total_records,
            "total_pages": total_pages,
            "page": pagination_params.page,
            "page_size": pagination_params.page_size,
            "data": response_data,
        }
        
        return success_response(
            data=response_data_with_meta,
            message=f"Destinos para el motivo ID {pagination_params.id_motivo} paginados obtenidos",
        )
    except RepositoryError as e:
        return error_response(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )