from sqlalchemy import Column, Integer, Date, DateTime, String, Index, DECIMAL, Float

from src.shared.database import _BaseMain
from datetime import datetime

class AreaOperariosORM(_BaseMain):
    __tablename__ = "fm_area_operarios"

    AREA_ID = Column(Integer, primary_key=True, autoincrement=True)
    AREA_NOMBRE = Column(String(100), nullable=False)
    AREA_ESTADO = Column(String(20), default='ACTIVO')

    AREA_FECCRE = Column(DateTime, default=datetime.now)
    AREA_FECMOD = Column(DateTime, nullable=True)

class ControlLoteAsiglineaORM(_BaseMain):
    __tablename__ = "fm_control_lote_asiglinea"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha_p = Column(Date)
    lote = Column(String(255))
    linea = Column(String(255))
    estado = Column(String(50))
    fecha_asig = Column(DateTime)
    tipo_limpieza = Column(Integer)
    turno = Column(Integer)

    __table_args__ = (Index('idx_fecha_p_lote_linea', 'fecha_p', 'lote', 'linea'),)

class EspeciesORM(_BaseMain):
    __tablename__ = "fm_especies"

    especie_id = Column(Integer, primary_key=True, autoincrement=True)
    especie_nombre = Column(String(100), unique=True, nullable=False)
    especie_familia = Column(String(100))
    especie_rend_normal = Column(DECIMAL(precision=20, scale=10))
    especie_merm_coccion = Column(DECIMAL(precision=20, scale=10))
    especie_kilos_horas = Column(DECIMAL(precision=20, scale=10))
    especie_piezas = Column(DECIMAL(precision=20, scale=10))
    especie_peso_promed = Column(DECIMAL(precision=20, scale=10))
    especie_peso_crudo = Column(DECIMAL(precision=20, scale=10))
    especie_rendimiento = Column(DECIMAL(precision=20, scale=10))
    especie_time_limpieza = Column(DECIMAL(precision=20, scale=10))
    especies_kilos_horas_media = Column(DECIMAL(precision=20, scale=10))
    especies_kilos_horas_doble = Column(DECIMAL(precision=20, scale=10))

class PlanningTurnoORM(_BaseMain):
    __tablename__ = "fm_planning_fnturno"

    plnn_id = Column(Integer, primary_key=True, autoincrement=True)
    plnn_fecha_p = Column(Date)
    plnn_turno = Column(Integer)
    plnn_linea = Column(String(255))
    plnn_hora_fin = Column(DateTime)

    __table_args__ = (Index('idx_fecha_p_linea_turno', 'plnn_fecha_p', 'plnn_linea', 'plnn_turno'),)

class DetalleProduccionORM(_BaseMain):
    __tablename__ = "fm_detalle_produccion"

    DPRO_ID = Column(Integer,primary_key=True,autoincrement=True)
    DPRO_FECPROD = Column(Date)
    DPRO_LOTE = Column(String(50))
    DPRO_PMIGA = Column(Float,nullable=True)
    DPRO_PPANZA = Column(Float,nullable=True)
    DPRO_PDESPERDICIO = Column(Float,nullable=True)
    DPRO_LINEA = Column(Integer,nullable=False)
    DPRO_TURNOX = Column(Integer,nullable=True)

    __table_args__ = (Index('DPRO_FECPROD', 'DPRO_LOTE','DPRO_LINEA'),)

class TipoLimpiezaORM(_BaseMain):
    __tablename__ = "cfg_tipo_limpieza"

    id_tipo_limpieza = Column(Integer, primary_key=True)
    nombre = Column(String(50))
    estado = Column(String(20))