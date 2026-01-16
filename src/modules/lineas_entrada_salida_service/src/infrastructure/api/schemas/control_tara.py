from typing import Optional

from pydantic import BaseModel


class TaraResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    peso_kg: float
    is_active: bool
    is_principal: bool

    class Config:
        from_attributes = True

class TaraCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    peso_kg: float

class TaraPrincipalRequest(BaseModel):
    is_principal: bool