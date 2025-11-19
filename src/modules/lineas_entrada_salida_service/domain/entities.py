from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Optional

@dataclass
class LineasEntrada:
    id: int
    fecha_p: Optional[date]
    fecha: Optional[datetime]
    peso_kg: Optional[float]
    turno: Optional[int]
    codigo_secuencia: Optional[str]
    codigo_parrilla: Optional[str]
    p_lote: Optional[str]
    hora_inicio: Optional[time]
    guid: Optional[str]

@dataclass
class LineasSalida:
    id: int
    fecha_p: Optional[date]
    fecha: Optional[datetime]
    peso_kg: Optional[float]
    codigo_bastidor: Optional[str]
    p_lote: Optional[str]
    codigo_parrilla: Optional[str]
    codigo_obrero: Optional[str]
    guid: Optional[str]

@dataclass
class ControlTara:
    id: int
    peso_kg: Optional[float]
    is_active: bool