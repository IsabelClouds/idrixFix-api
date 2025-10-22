from pydantic import BaseModel, Field, conint
from typing import Optional, List
from datetime import date, datetime
from src.modules.management_service.src.domain.entities import TipoMovimiento

class WorkerMovementBase(BaseModel):
    linea: str = Field(..., max_length=255)
    fecha_p: date
    # Usamos el Enum directamente en Pydantic para validación
    tipo_movimiento: TipoMovimiento 
    motivo: str = Field(..., max_length=255)
    codigo_operario: str = Field(..., max_length=255)
    destino: Optional[str] = Field(None, max_length=255)
    hora: datetime 
    observacion: Optional[str] = Field(None, max_length=255)


class WorkerMovementCreate(WorkerMovementBase):
    pass


class WorkerMovementUpdate(BaseModel):
    # Permite actualizar cualquier campo, todos opcionales
    linea: Optional[str] = Field(None, max_length=255)
    fecha_p: Optional[date] = None
    tipo_movimiento: Optional[str] = Field(None, max_length=50)
    motivo: Optional[str] = Field(None, max_length=255)
    codigo_operario: Optional[str] = Field(None, max_length=255)
    destino: Optional[str] = Field(None, max_length=255)
    hora: Optional[datetime] = None
    observacion: Optional[str] = Field(None, max_length=255)


class WorkerMovementResponse(WorkerMovementBase):
    id: int
    class Config:
        from_attributes = True
# Schema para la entrada de filtros (para conteo y paginación)
class WorkerMovementFilters(BaseModel):
    fecha_inicial: Optional[date] = None
    fecha_final: Optional[date] = None
    linea: Optional[str] = None
    codigo_operario: Optional[str] = Field(None, max_length=255)


# Schema para la paginación
class WorkerMovementPagination(WorkerMovementFilters):
    page: conint(ge=1) = 1 # Página actual (mínimo 1)
    page_size: conint(ge=1) = 20 # Tamaño de página (mínimo 1)


# Schema de respuesta para la paginación (útil para el front-end)
class WorkerMovementPaginatedResponse(BaseModel):
    total_records: int
    total_pages: int
    page: int
    page_size: int
    data: List[WorkerMovementResponse]

# Schemas de RefMotivo
class RefMotivoBase(BaseModel):
    descripcion: str = Field(..., max_length=100)
    tipo_motivo: str = Field(..., max_length=10)
    es_justificado: bool = False
    estado: str = Field("ACTIVO", max_length=10)

class RefMotivoResponse(RefMotivoBase):
    id_motivo: int
    class Config:
        from_attributes = True

# Filtros para Motivos (Solo incluye paginación, el filtro de estado es implícito)
class RefMotivoFilters(BaseModel):
    pass 

class RefMotivoPagination(RefMotivoFilters):
    page: conint(ge=1) = 1
    page_size: conint(ge=1) = 20


# Schemas de RefDestinoMotivo
class RefDestinoMotivoBase(BaseModel):
    id_motivo: int = Field(..., ge=1)
    nombre_destino: str = Field(..., max_length=100)
    descripcion: Optional[str] = Field(None, max_length=200)
    estado: str = Field("ACTIVO", max_length=10)

class RefDestinoMotivoResponse(RefDestinoMotivoBase):
    id_destino: int
    class Config:
        from_attributes = True

# Filtros para Destinos por Motivo (Requiere id_motivo)
class RefDestinoMotivoFilters(BaseModel):
    id_motivo: int = Field(..., description="ID del motivo para filtrar destinos.", ge=1)

class RefDestinoMotivoPagination(RefDestinoMotivoFilters):
    page: conint(ge=1) = 1
    page_size: conint(ge=1) = 20
    
    
# Schema de respuesta para la paginación (Genérico)
class PaginatedResponse(BaseModel):
    total_records: int
    total_pages: int
    page: int
    page_size: int