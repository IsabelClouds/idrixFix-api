from datetime import date
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
