from sqlalchemy import create_engine, Column, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from .config import settings

# Configuración específica para SQL Server
engine_main = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocalMain = sessionmaker(autocommit=False, autoflush=False, bind=engine_main)
BaseMain = declarative_base()

# --- Conexión a la Base de Datos de Autenticación (NUEVO) ---
engine_auth = create_engine(settings.auth_database_url, pool_pre_ping=True)
SessionLocalAuth = sessionmaker(autocommit=False, autoflush=False, bind=engine_auth)
BaseAuth = declarative_base()

# Clase base declarativa
_BaseMain = BaseMain
_BaseAuth = BaseAuth