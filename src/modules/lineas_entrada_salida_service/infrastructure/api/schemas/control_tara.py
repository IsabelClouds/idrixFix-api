from typing import Optional

from pydantic import BaseModel


class TaraResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    peso_kg: float
    is_active: bool

    class Config:
        from_attributes = True

class TaraCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    peso_kg: float