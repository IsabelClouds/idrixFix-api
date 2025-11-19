from typing import Optional

from pydantic import BaseModel


class TaraResponse(BaseModel):
    id: int
    peso_kg: Optional[float]
    is_active: bool

    class Config:
        from_attributes = True

class TaraCreate(BaseModel):
    peso_kg: Optional[float]