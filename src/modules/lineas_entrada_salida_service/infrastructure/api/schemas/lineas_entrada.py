from datetime import date, datetime, time
from pydantic import BaseModel
from typing import Optional, List


class LineasEntradaResponse(BaseModel):
    id: int
    fecha_p: Optional[date]
    fecha: Optional[datetime]
    peso_kg: Optional[float]
    turno: Optional[int]
    codigo_secuencia: Optional[str]
    codigo_parrilla: Optional[str]
    p_lote: Optional[str]
    hora_inicio: Optional[time]
    guid: Optional[str]

    class Config:
        from_attributes = True

class LineasEntradaUpdate(BaseModel):
    turno: Optional[int]
    p_lote: Optional[str]
    hora_inicio: Optional[time]

class LineasEntradaPaginatedResponse(BaseModel):
    total_records: int
    total_pages: int
    page: int
    page_size: int
    data: List[LineasEntradaResponse]
