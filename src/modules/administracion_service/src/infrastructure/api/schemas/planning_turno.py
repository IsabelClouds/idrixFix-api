from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, conint


class PlanningTurnoResponse(BaseModel):
    plnn_id: int
    plnn_fecha_p: Optional[date] = None
    plnn_turno: Optional[int] = None
    plnn_linea: Optional[str] = None
    plnn_hora_fin: Optional[datetime] = None

    class Config:
        from_attributes = True

class PlanningTurnoUpdate(BaseModel):
    plnn_turno: Optional[int] = None
    plnn_linea: Optional[str] = None
    plnn_hora_fin: Optional[datetime] = None

class PlanningTurnoFilters(BaseModel):
    fecha_p: date
    turno: Optional[int] = None
    linea: Optional[str] = None

class PlanningTurnoPagination(PlanningTurnoFilters):
    page: conint(ge=1) = 1
    page_size: conint(ge=1) = 20