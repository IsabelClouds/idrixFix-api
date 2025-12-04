from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AreaOperariosResponse(BaseModel):
    area_id: int
    area_nombre: Optional[str]
    area_estado: Optional[str]
    area_feccre: Optional[datetime]
    area_fecmod: Optional[datetime]

    class Config:
        from_attributes = True

class AreaOperariosRequest(BaseModel):
    area_nombre: Optional[str]

