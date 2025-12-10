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
    lote: Optional[str]
    linea: Optional[str]
    estado: Optional[str]
    fecha_asig: Optional[datetime]
    tipo_limpieza: Optional[int]
    turno: Optional[int]

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

@dataclass
class Linea:
    line_id: int
    line_nombre: str
    line_estado: Optional[str]
    line_feccre: datetime
    line_fecmod: Optional[datetime]
    line_planta: Optional[int]

@dataclass
class Planta:
    plan_id: int
    plan_nombre: str
    plan_estado: Optional[str] = None
    plan_feccre: Optional[datetime] = None
    plan_fecmod: Optional[datetime] = None

@dataclass
class PlanningTurno:
    plnn_id: int
    plnn_fecha_p: Optional[date] = None
    plnn_turno: Optional[int] = None
    plnn_linea: Optional[str] = None
    plnn_hora_fin: Optional[datetime] = None

@dataclass
class DetalleProduccion:
    dpro_id: int
    dpro_linea: int
    dpro_fecprod: Optional[date] = None
    dpro_lote: Optional[str] = None
    dpro_pmiga: Optional[float] = None
    dpro_ppanza: Optional[float] = None
    dpro_pdesperdicio: Optional[float] = None
    dpro_turnox: Optional[int] = None

@dataclass
class TipoLimpieza:
    id_tipo_limpieza: int
    nombre: Optional[str] = None
    estado: Optional[str] = None
