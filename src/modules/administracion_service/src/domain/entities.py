from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AreaOperarios:
    area_id: int
    area_nombre: Optional[str]
    area_estado: Optional[str]
    area_feccre: Optional[datetime]
    area_fecmod: Optional[datetime]