from sqlalchemy import Column, Integer, Date, DateTime, Float, String, Time, Boolean

from src.shared.database import _BaseAuth, _BaseMain

#Lineas Entrada
class LineaUnoEntradaORM(_BaseMain):
    __tablename__ = "reg_linea_uno_entrad"

    id = Column(Integer, primary_key=True)
    fecha_p = Column(Date)
    fecha = Column(DateTime)
    peso_kg = Column(Float)
    turno = Column(Integer)
    codigo_secuencia = Column(String(255))
    codigo_parrilla = Column(String(255))
    p_lote = Column(String(100))
    hora_inicio = Column(Time)
    guid = Column(String(255))

class LineaDosEntradaORM(_BaseMain):
    __tablename__ = "reg_linea_dos_entrad"

    id = Column(Integer, primary_key=True)
    fecha_p = Column(Date)
    fecha = Column(DateTime)
    peso_kg = Column(Float)
    turno = Column(Integer)
    codigo_secuencia = Column(String(255))
    codigo_parrilla = Column(String(255))
    p_lote = Column(String(100))
    hora_inicio = Column(Time)
    guid = Column(String(255))

class LineaTresEntradaORM(_BaseMain):
    __tablename__ = "reg_linea_tres_entrad"

    id = Column(Integer, primary_key=True)
    fecha_p = Column(Date)
    fecha = Column(DateTime)
    peso_kg = Column(Float)
    turno = Column(Integer)
    codigo_secuencia = Column(String(255))
    codigo_parrilla = Column(String(255))
    p_lote = Column(String(100))
    hora_inicio = Column(Time)
    guid = Column(String(255))

class LineaCuatroEntradaORM(_BaseMain):
    __tablename__ = "reg_linea_cuatro_entrad"

    id = Column(Integer, primary_key=True)
    fecha_p = Column(Date)
    fecha = Column(DateTime)
    peso_kg = Column(Float)
    turno = Column(Integer)
    codigo_secuencia = Column(String(255))
    codigo_parrilla = Column(String(255))
    p_lote = Column(String(100))
    hora_inicio = Column(Time)
    guid = Column(String(255))

class LineaCincoEntradaORM(_BaseMain):
    __tablename__ = "reg_linea_cinco_entrad"

    id = Column(Integer, primary_key=True)
    fecha_p = Column(Date)
    fecha = Column(DateTime)
    peso_kg = Column(Float)
    turno = Column(Integer)
    codigo_secuencia = Column(String(255))
    codigo_parrilla = Column(String(255))
    p_lote = Column(String(100))
    hora_inicio = Column(Time)
    guid = Column(String(255))

class LineaSeisEntradaORM(_BaseMain):
    __tablename__ = "reg_linea_seis_entrad"

    id = Column(Integer, primary_key=True)
    fecha_p = Column(Date)
    fecha = Column(DateTime)
    peso_kg = Column(Float)
    turno = Column(Integer)
    codigo_secuencia = Column(String(255))
    codigo_parrilla = Column(String(255))
    p_lote = Column(String(100))
    hora_inicio = Column(Time)
    guid = Column(String(255))

#Lineas Salida
class LineaUnoSalidaORM(_BaseMain):
    __tablename__ = "reg_linea_uno_salid"

    id = Column(Integer, primary_key=True)
    fecha_p = Column(Date)
    fecha = Column(DateTime)
    peso_kg = Column(Float)
    codigo_bastidor = Column(String(255))
    p_lote = Column(String(100))
    codigo_parrilla = Column(String(255))
    codigo_obrero = Column(String(255))
    guid = Column(String(255))

class LineaDosSalidaORM(_BaseMain):
    __tablename__ = "reg_linea_dos_salid"

    id = Column(Integer, primary_key=True)
    fecha_p = Column(Date)
    fecha = Column(DateTime)
    peso_kg = Column(Float)
    codigo_bastidor = Column(String(255))
    p_lote = Column(String(100))
    codigo_parrilla = Column(String(255))
    codigo_obrero = Column(String(255))
    guid = Column(String(255))

class LineaTresSalidaORM(_BaseMain):
    __tablename__ = "reg_linea_tres_salid"

    id = Column(Integer, primary_key=True)
    fecha_p = Column(Date)
    fecha = Column(DateTime)
    peso_kg = Column(Float)
    codigo_bastidor = Column(String(255))
    p_lote = Column(String(100))
    codigo_parrilla = Column(String(255))
    codigo_obrero = Column(String(255))
    guid = Column(String(255))

class LineaCuatroSalidaORM(_BaseMain):
    __tablename__ = "reg_linea_cuatro_salid"

    id = Column(Integer, primary_key=True)
    fecha_p = Column(Date)
    fecha = Column(DateTime)
    peso_kg = Column(Float)
    codigo_bastidor = Column(String(255))
    p_lote = Column(String(100))
    codigo_parrilla = Column(String(255))
    codigo_obrero = Column(String(255))
    guid = Column(String(255))

class LineaCincoSalidaORM(_BaseMain):
    __tablename__ = "reg_linea_cinco_salid"

    id = Column(Integer, primary_key=True)
    fecha_p = Column(Date)
    fecha = Column(DateTime)
    peso_kg = Column(Float)
    codigo_bastidor = Column(String(255))
    p_lote = Column(String(100))
    codigo_parrilla = Column(String(255))
    codigo_obrero = Column(String(255))
    guid = Column(String(255))

class LineaSeisSalidaORM(_BaseMain):
    __tablename__ = "reg_linea_seis_salid"

    id = Column(Integer, primary_key=True)
    fecha_p = Column(Date)
    fecha = Column(DateTime)
    peso_kg = Column(Float)
    codigo_bastidor = Column(String(255))
    p_lote = Column(String(100))
    codigo_parrilla = Column(String(255))
    codigo_obrero = Column(String(255))
    guid = Column(String(255))

# Control Tara
class ControlTaraOrm(_BaseAuth):
    __tablename__ = "control_tara"

    id = Column(Integer, primary_key=True)
    peso_kg = Column(Float)
    is_active = Column(Boolean, nullable=False, default=True)