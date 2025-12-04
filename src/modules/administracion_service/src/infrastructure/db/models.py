from sqlalchemy import Column, Integer, Date, DateTime, Float, String, Time, Boolean
from src.shared.database import _BaseMain
from datetime import datetime

class AreaOperariosORM(_BaseMain):
    __tablename__ = "fm_area_operarios"

    AREA_ID = Column(Integer, primary_key=True, autoincrement=True)
    AREA_NOMBRE = Column(String(100), nullable=False)
    AREA_ESTADO = Column(String(20), default='ACTIVO')

    AREA_FECCRE = Column(DateTime, default=datetime.now)
    AREA_FECMOD = Column(DateTime, nullable=True)