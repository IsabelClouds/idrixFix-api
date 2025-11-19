from sqlalchemy import (
    Column,
    String,
    BigInteger,
    Integer,
    Float,
    Boolean,
    DateTime,
    Text,
    JSON,
    ForeignKey,
    UniqueConstraint,
    ForeignKeyConstraint,
    Enum as SQLEnum,
)
from sqlalchemy.sql import func, false
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from src.shared.database import _BaseAuth, _BaseMain
from src.modules.auth_service.src.domain.entities import ModuloEnum, PermisoEnum
import enum
import datetime


class Usuario(_BaseAuth):
    __tablename__ = "usuarios"
    
    id_usuario = Column(BigInteger, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Foreign Key a Rol
    id_rol = Column(BigInteger, ForeignKey("roles.id_rol"), nullable=True)
    is_superuser = Column(Boolean, nullable=False, default=False, server_default=false())
    
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Relación muchos-a-uno: Un usuario tiene un rol
    rol = relationship("Rol", back_populates="usuarios")
    
    # Relación uno-a-muchos: Un usuario puede tener muchas sesiones
    sesiones = relationship("SesionUsuario", back_populates="usuario")
    
    # Relación uno-a-muchos: Un usuario puede tener muchas líneas asignadas
    lineas_asignadas = relationship("UsuarioLineaAsignada", back_populates="usuario")
    # Relación uno-a-muchos: Un usuario puede tener muchos turnos asignados
    turnos_asignados = relationship("UsuarioTurnoAsignado", back_populates="usuario")

    @hybrid_property
    def permisos_modulos(self):
        """Obtiene los permisos por módulo del usuario basado en su rol"""
        if not self.rol or not self.rol.permisos_modulo:
            return []
        
        modulos = []
        for permiso_modulo in self.rol.permisos_modulo:
            if permiso_modulo.is_active:
                # Los permisos se almacenan como JSON, pueden ser lista de strings o lista de enums
                permisos_lista = permiso_modulo.permisos
                if isinstance(permisos_lista, list):
                    # Si son enums, convertir a strings
                    permisos_strings = [p.value if hasattr(p, 'value') else p for p in permisos_lista]
                else:
                    permisos_strings = permisos_lista
                
                modulos.append({
                    "nombre": permiso_modulo.modulo.value if hasattr(permiso_modulo.modulo, 'value') else permiso_modulo.modulo,
                    "permisos": permisos_strings
                })
        
        return modulos
    @hybrid_property
    def ids_lineas_externas(self):
        """Obtiene solo los IDs de las líneas externas asignadas"""
        if not self.lineas_asignadas:
            return []
        return [linea.id_linea_externa for linea in self.lineas_asignadas]


class Rol(_BaseAuth):
    __tablename__ = "roles"
    
    id_rol = Column(BigInteger, primary_key=True)
    nombre = Column(String(50), unique=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Relación uno-a-muchos: Un rol tiene muchos usuarios
    usuarios = relationship("Usuario", back_populates="rol")
    
    # Relación uno-a-muchos: Un rol tiene muchos permisos de módulo
    permisos_modulo = relationship("PermisoModulo", back_populates="rol")


class PermisoModulo(_BaseAuth):
    __tablename__ = "permisos_modulo"
    
    id_permiso_modulo = Column(BigInteger, primary_key=True)
    
    # Foreign Key a Rol
    id_rol = Column(BigInteger, ForeignKey("roles.id_rol"), nullable=False)
    
    # Módulo del sistema (enum)
    modulo = Column(SQLEnum(ModuloEnum), nullable=False)
    
    # Lista de permisos como JSON (read, write)
    permisos = Column(JSON, nullable=False)
    
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Relación muchos-a-uno: Un permiso pertenece a un rol
    rol = relationship("Rol", back_populates="permisos_modulo")
    
    # Constraint de unicidad: un rol no puede tener permisos duplicados para el mismo módulo
    __table_args__ = (
        UniqueConstraint("id_rol", "modulo", name="uq_rol_modulo"),
    )


class SesionUsuario(_BaseAuth):
    __tablename__ = "sesiones_usuario"
    
    id_sesion = Column(BigInteger, primary_key=True)
    
    # Foreign Key a Usuario
    id_usuario = Column(BigInteger, ForeignKey("usuarios.id_usuario"), nullable=False)
    
    token = Column(String(500), unique=True, nullable=False)
    refresh_token = Column(String(500), nullable=True)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_expiracion = Column(DateTime, nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Relación muchos-a-uno: Una sesión pertenece a un usuario
    usuario = relationship("Usuario", back_populates="sesiones")

class UsuarioLineaAsignada(_BaseAuth):
    """
    Tabla de unión que asigna líneas de trabajo (de la DB externa) 
    a los usuarios (de la DB interna).
    """
    __tablename__ = "usuario_lineas_asignadas"
    
    id_usuario_linea = Column(BigInteger, primary_key=True)
    
    # 1. Relación con tu Usuario interno
    id_usuario = Column(BigInteger, ForeignKey("usuarios.id_usuario"), nullable=False)
    
    # 2. ID de la línea de trabajo externa (¡NO es una FK de base de datos!)
    id_linea_externa = Column(Integer, nullable=False) 
    
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.now())
    
    # Relación para que SQLAlchemy la entienda
    usuario = relationship("Usuario", back_populates="lineas_asignadas")
    
    # Constraint para evitar duplicados
    __table_args__ = (
        UniqueConstraint("id_usuario", "id_linea_externa", name="uq_usuario_linea_externa"),
    )

class AuditoriaLogORM(_BaseAuth):
    """
    Tabla para registrar logs de auditoría de creación y actualización
    de registros en ambas bases de datos.
    """
    __tablename__ = "auditoria_logs"
    
    log_id = Column(BigInteger, primary_key=True)
    modelo = Column(String(100), nullable=False, index=True) # ej. "WorkerMovementORM"
    entidad_id = Column(String(100), nullable=False, index=True) # El ID del registro afectado
    accion = Column(String(50), nullable=False, index=True) # "CREATE", "UPDATE"
    
    # JSON para los datos
    datos_anteriores = Column(JSON, nullable=True) # Null en CREATE
    datos_nuevos = Column(JSON, nullable=True)
    
    # Quién lo hizo (ID y JSON snapshot)
    ejecutado_por_id = Column(BigInteger, ForeignKey("usuarios.id_usuario"), nullable=True)
    ejecutado_por_json = Column(JSON, nullable=True)
    
    fecha = Column(DateTime, nullable=False, default=datetime.datetime.now())
    
    usuario = relationship("Usuario")


## LINEAS 
class LineaORM(_BaseMain):
    __tablename__ = "fm_lineas_operarios"

    LINE_ID = Column(Integer,primary_key=True,autoincrement=True)
    LINE_NOMBRE = Column(String(100),nullable=False)
    LINE_ESTADO = Column(String(20),default='ACTIVO')
    
    LINE_FECCRE = Column(DateTime,default=datetime.datetime.now)
    LINE_FECMOD = Column(DateTime,nullable=True)
    
    LINE_PLANTA = Column(Integer,ForeignKey("fm_planta_operarios.PLAN_ID"))
    planta = relationship("PlantaORM", back_populates="lineas")


class PlantaORM(_BaseMain):
    __tablename__ = "fm_planta_operarios"

    PLAN_ID = Column(Integer,primary_key=True,autoincrement=True)
    PLAN_NOMBRE = Column(String(100),nullable=False)
    PLAN_ESTADO = Column(String(20),default='ACTIVO')
    PLAN_FECCRE = Column(DateTime,default=datetime.datetime.now)
    PLAN_FECMOD = Column(DateTime,nullable=True)

    lineas = relationship("LineaORM", back_populates="planta")

## TURNOS
class TurnoORM(_BaseMain):
    __tablename__ = "fm_turnos_operarios"

    TURN_ID = Column(Integer,primary_key=True,autoincrement=True)
    TURN_NOMBRE = Column(String(100),nullable=False)
    TURN_ESTADO = Column(String(20),default='ACTIVO')
    
    TURN_FECCRE = Column(DateTime,default=datetime.datetime.now)
    TURN_FECMOD = Column(DateTime,nullable=True)

class UsuarioTurnoAsignado(_BaseAuth):
    """
    Tabla de unión que asigna turnos (de la DB externa) 
    a los usuarios (de la DB interna).
    """
    __tablename__ = "usuario_turnos_asignados"
    
    id_usuario_turno = Column(BigInteger, primary_key=True)
    
    # 1. Relación con tu Usuario interno
    id_usuario = Column(BigInteger, ForeignKey("usuarios.id_usuario"), nullable=False, index=True)
    
    # 2. ID del turno externo (coincide con TURN_ID de TurnoORM)
    id_turno_externo = Column(Integer, nullable=False, index=True) 
    
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.now)
    
    # Relación para que SQLAlchemy la entienda
    usuario = relationship("Usuario", back_populates="turnos_asignados")
    
    # Constraint para evitar duplicados
    __table_args__ = (
        UniqueConstraint("id_usuario", "id_turno_externo", name="uq_usuario_turno_externo"),
    )