from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, conint


class LineasFilters(BaseModel):
    fecha: Optional[date] = None
    lote: Optional[str] = None

class LineasPagination(LineasFilters):
    page: conint(ge=1) = 1
    page_size: conint(ge=1) = 20

class UpdateCodigoParrillaRequest(BaseModel):
    valor: int

class LineaEnum(int, Enum):
    L1 = 1
    L2 = 2
    L3 = 3
    L4 = 4
    L5 = 5
    L6 = 6