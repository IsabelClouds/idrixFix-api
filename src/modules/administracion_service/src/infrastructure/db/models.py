from sqlalchemy import Column, Integer, Date, DateTime, Float, String, Time, Boolean, Index
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