from pydantic import BaseModel, Field, conint
from typing import Optional, List, Dict, Any
from datetime import date, datetime

# --- Schemas para AuditoriaLog ---

class AuditoriaLogFilters(BaseModel):
    """Filtros para buscar logs de auditoría."""
    ejecutado_por_id: Optional[int] = Field(None, description="ID del usuario que ejecutó la acción.")
    accion: Optional[str] = Field(None, max_length=50, description="Tipo de acción (CREATE, UPDATE, DELETE).")
    modelo: Optional[str] = Field(None, max_length=100, description="Nombre del modelo/tabla afectado.")
    fecha: Optional[date] = Field(None, description="Fecha específica (YYYY-MM-DD) en que ocurrió la acción.")

class AuditoriaLogPagination(AuditoriaLogFilters):
    """Parámetros de paginación para logs de auditoría."""
    page: conint(ge=1) = 1
    page_size: conint(ge=1) = 20

class AuditoriaLogResponse(BaseModel):
    """Schema de respuesta para un log de auditoría."""
    log_id: int
    modelo: str
    entidad_id: str
    accion: str
    datos_anteriores: Optional[Dict[str, Any]] = None
    datos_nuevos: Optional[Dict[str, Any]] = None
    ejecutado_por_id: Optional[int] = None
    ejecutado_por_json: Optional[Dict[str, Any]] = None
    fecha: datetime

    class Config:
        from_attributes = True # Para mapear desde el ORM

class AuditoriaLogPaginatedResponse(BaseModel):
    """Schema de respuesta para logs de auditoría paginados."""
    total_records: int
    total_pages: int
    page: int
    page_size: int
    data: List[AuditoriaLogResponse]