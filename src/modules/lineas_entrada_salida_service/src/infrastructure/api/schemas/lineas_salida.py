from datetime import date, datetime
from pydantic import BaseModel, Field
from typing import Optional, List

from src.modules.lineas_entrada_salida_service.src.infrastructure.api.schemas.lineas_shared import LineasFilters, \
    LineaEnum


class LineasSalidaResponse(BaseModel):
    id: int
    fecha_p: Optional[date]
    fecha: Optional[datetime]
    peso_kg: Optional[float]
    codigo_bastidor: Optional[str]
    p_lote: Optional[str]
    codigo_parrilla: Optional[str]
    codigo_obrero: Optional[str]
    guid: Optional[str]

    class Config:
        from_attributes = True

class LineasSalidaUpdate(BaseModel):
    codigo_bastidor: Optional[str]
    p_lote: Optional[str]

class LineasSalidaPaginatedResponse(BaseModel):
    total_records: int
    total_pages: int
    page: int
    page_size: int
    data: List[LineasSalidaResponse]

class TaraIdRequest(BaseModel):
    tara_id: int

class PanzaRequest(LineasFilters):
    peso_kg: float

class UpdateLoteRequest(BaseModel):
    ids: List[int] = Field(..., min_items=1)
    lote: str

class MigaResponse(BaseModel):
    id: int
    linea: LineaEnum
    registro: int
    p_miga: float
    porcentaje: float

class MigaRequest(BaseModel):
    linea_id: int
    tara_id: int
    p_miga: float

class LineasSalidaMigaResponse(LineasSalidaResponse):
    p_miga: float
    porcentaje: float

class LineasSalidaMigaPaginatedResponse(BaseModel):
    total_records: int
    total_pages: int
    page: int
    page_size: int
    data: List[LineasSalidaMigaResponse]

