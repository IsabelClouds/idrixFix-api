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

@dataclass
class Especie:
    especie_id: int
    especie_nombre: str
    especie_familia: Optional[str] = None
    especie_rend_normal: Optional[float] = None
    especie_merm_coccion: Optional[float] = None
    especie_kilos_horas: Optional[float] = None
    especie_piezas: Optional[float] = None
    especie_peso_promed: Optional[float] = None
    especie_peso_crudo: Optional[float] = None
    especie_rendimiento: Optional[float] = None
    especie_time_limpieza: Optional[float] = None
    especies_kilos_horas_media: Optional[float] = None
    especies_kilos_horas_doble: Optional[float] = None