from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional


@dataclass
class AreaOperarios:
    area_id: int
    area_nombre: Optional[str]
    area_estado: Optional[str]
    area_feccre: Optional[datetime]
    area_fecmod: Optional[datetime]

@dataclass
class ControlLoteAsiglinea:
    id: int
    fecha_p: Optional[date]
    lote : Optional[str]
    linea : Optional[str]
    estado : Optional[str]
    fecha_asig : Optional[datetime]
    tipo_limpieza : Optional[int]
    turno : Optional[int]