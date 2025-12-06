from typing import Optional

from pydantic import BaseModel, conint


class EspeciesResponse(BaseModel):
    especie_id: int
    especie_nombre: str
    especie_familia: Optional[str] = None
    especie_kilos_horas: Optional[float] = None
    especies_kilos_horas_media: Optional[float] = None
    especies_kilos_horas_doble: Optional[float] = None

    class Config:
        from_attributes = True


class EspeciesRequest(BaseModel):
    especie_nombre: str
    especie_familia: Optional[str]
    especie_kilos_horas: Optional[float]
    especies_kilos_horas_media: Optional[float]
    especies_kilos_horas_doble: Optional[float]

class EspeciesPaginated(BaseModel):
    page: conint(ge=1) = 1
    page_size: conint(ge=1) = 20
