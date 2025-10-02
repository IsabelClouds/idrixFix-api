from sqlalchemy import (
    Column,
    String,
    BigInteger,
    Boolean,
    DateTime,
    Text,
    JSON,
    ForeignKey,
    UniqueConstraint,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from src.shared.database import _BaseAuth
from src.modules.auth_service.src.domain.entities import ModuloEnum, PermisoEnum
import enum


class Usuario(_BaseAuth):
    __tablename__ = "usuarios"
    
    id_usuario = Column(BigInteger, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Foreign Key a Rol
    id_rol = Column(BigInteger, ForeignKey("roles.id_rol"), nullable=True)
    
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Relación muchos-a-uno: Un usuario tiene un rol
    rol = relationship("Rol", back_populates="usuarios")
    
    # Relación uno-a-muchos: Un usuario puede tener muchas sesiones
    sesiones = relationship("SesionUsuario", back_populates="usuario")
    
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
                    "ruta": permiso_modulo.ruta,
                    "permisos": permisos_strings
                })
        
        return modulos


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
    
    # Ruta del módulo
    ruta = Column(String(100), nullable=False)
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
