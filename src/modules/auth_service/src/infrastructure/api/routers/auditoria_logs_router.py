from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from src.shared.base import get_auth_db # Usamos la DB de autenticación
from src.shared.common.responses import success_response, error_response
from src.shared.exceptions import RepositoryError
import traceback

# proteger estos endpoints)
from src.shared.security import get_current_user_data 

# Importar dependencia del AuditUseCase
from src.modules.auth_service.src.infrastructure.api.routers.lineas_asignadas_router import get_audit_use_case
from src.modules.auth_service.src.application.use_cases.audit_use_case import AuditUseCase

# Importar Schemas
from src.modules.auth_service.src.infrastructure.api.schemas.auditoria import (
    AuditoriaLogFilters,
    AuditoriaLogPagination,
    AuditoriaLogResponse,
)

router = APIRouter()
@router.post("/total", status_code=status.HTTP_200_OK) 
def get_total_logs_by_filters(
    filters: AuditoriaLogFilters,
    use_case: AuditUseCase = Depends(get_audit_use_case),
    user_data: Dict[str, Any] = Depends(get_current_user_data)
):
    """Obtiene el número total de logs de auditoría según los filtros."""
    try:
        total_records = use_case.count_logs_by_filters(filters)
        return success_response(
            data=total_records,
            message="Total de logs obtenido",
        )
    except RepositoryError as e:
        return error_response(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
         return error_response(message=str(e), detail=traceback.format_exc(), status_code=500)


@router.post("/paginated", status_code=status.HTTP_200_OK)
def get_logs_paginated(
    pagination_params: AuditoriaLogPagination,
    use_case: AuditUseCase = Depends(get_audit_use_case),
    user_data: Dict[str, Any] = Depends(get_current_user_data)
):
    """Obtiene los logs de auditoría paginados según los filtros."""
    try:
        pagination_result = use_case.get_logs_paginated_by_filters(pagination_params)
        
        # Mapeamos los ORMs ('data') a los schemas de respuesta
        response_data = [
            AuditoriaLogResponse.model_validate(log_orm).model_dump(mode="json")
            for log_orm in pagination_result["data"]
        ]
        
        # Construimos la respuesta final
        response_data_with_meta = {
            "total_records": pagination_result["total_records"],
            "total_pages": pagination_result["total_pages"],
            "page": pagination_result["page"],
            "page_size": pagination_result["page_size"],
            "data": response_data,
        }
        
        return success_response(
            data=response_data_with_meta,
            message="Logs paginados obtenidos",
        )
    except RepositoryError as e:
        return error_response(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
         return error_response(message=str(e), detail=traceback.format_exc(), status_code=500)