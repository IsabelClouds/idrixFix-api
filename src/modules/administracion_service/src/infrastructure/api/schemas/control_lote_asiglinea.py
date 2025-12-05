from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, conint


class ControlLoteAsiglineaResponse(BaseModel):
    id: int
    fecha_p: Optional[date]
    lote : Optional[str]
    linea : Optional[str]
    estado : Optional[str]
    fecha_asig : Optional[datetime]
    tipo_limpieza : Optional[int]
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
    PROCCESS = "PROCCESS"
    FINISHED = "FINISHED"
    STOPPED = "STOPPED"

from enum import Enum

class LineaEnum(int, Enum):
    L1 = 1
    L2 = 2
    L3 = 3
    L4 = 4
    L5 = 5
    L6 = 6

class TurnoEnum(int, Enum):
    T1 = 1
    T2 = 2

class ControlLoteAsiglineaUpdate(BaseModel):
    lote: Optional[str] = None
    estado: Optional[EstadoLote] = None
    linea: Optional[LineaEnum] = None
    tipo_limpieza : Optional[int] = None
    turno: Optional[TurnoEnum] = None


