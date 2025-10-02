from sqlalchemy import (
    Column,
    String,
    Date,
    ForeignKey,
    BigInteger,
    Integer,
    Boolean,
    DateTime,
    UniqueConstraint,
    Index,
    Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from src.shared.database import _BaseMain
from src.modules.management_service.src.domain.entities import TipoMovimiento

class WorkerMovementORM(_BaseMain):
    __tablename__ = "fm_movimientos_operarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    linea = Column(String(255), nullable=False)
    fecha_p = Column(Date, nullable=False)
    tipo_movimiento = Column(SQLEnum(TipoMovimiento), nullable=False) 
    motivo = Column(String(255), nullable=False)
    codigo_operario = Column(String(255), nullable=False)
    destino = Column(String(255))
    hora = Column(DateTime, nullable=False)
    observacion = Column(String(255))

    __table_args__ = (Index('idx_fecha_p_linea_operario', 'fecha_p', 'linea', 'codigo_operario'),)