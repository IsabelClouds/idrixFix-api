from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, conint

from src.modules.administracion_service.src.infrastructure.api.schemas.shared import LineaEnum, TurnoEnum
from src.modules.administracion_service.src.infrastructure.api.schemas.tipo_limpieza import TipoLimpiezaResponse


class ControlLoteAsiglineaResponse(BaseModel):
    id: int
    fecha_p: Optional[date]
    lote : Optional[str]
    linea : Optional[str]
    estado : Optional[str]
    fecha_asig : Optional[datetime]
    tipo_limpieza : Optional[TipoLimpiezaResponse]
    turno : Optional[int]

    class Config:
        from_attributes = True

class ControlLoteAsiglineaFilters(BaseModel):
    fecha_p: date
    lote: Optional[str] = None
    linea: Optional[str] = None

class ControlLoteAsiglineaPagination(ControlLoteAsiglineaFilters):
    page: conint(ge=1) = 1
    page_size: conint(ge=1) = 20

class EstadoLote(str, Enum):
    PROCESS = "PROCESS"
    FINISHED = "FINISHED"
    STOPPED = "STOPPED"

class ControlLoteAsiglineaUpdate(BaseModel):
    lote: Optional[str] = None
    estado: Optional[EstadoLote] = None
    linea: Optional[LineaEnum] = None
    tipo_limpieza : Optional[int] = None
    turno: Optional[TurnoEnum] = None


