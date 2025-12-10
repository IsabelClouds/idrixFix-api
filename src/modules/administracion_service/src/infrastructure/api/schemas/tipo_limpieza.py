from typing import Optional

from pydantic import BaseModel


class TipoLimpiezaResponse(BaseModel):
    id_tipo_limpieza: int
    nombre: Optional[str] = None
    estado: Optional[str] = None

    class Config:
        from_attributes = True