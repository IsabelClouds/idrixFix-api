from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum


class ModuloEnum(Enum):
    """Enum para los módulos disponibles en el sistema"""
    CONFIGURACION = "CONFIGURACION"
    USUARIOS = "USUARIOS"
    ROLES = "ROLES"
    MARCACION = "MARCACION"
    MOVIMIENTOS = "MOVIMIENTOS"
    AUDITORIA = "AUDITORIA"
    PRODUCCION_LINEAS = "PRODUCCION_LINEAS"
    LINEA_UNO = "LINEA_UNO"
    LINEA_DOS = "LINEA_DOS"
    LINEA_TRES = "LINEA_TRES"
    LINEA_CUATRO = "LINEA_CUATRO"
    LINEA_CINCO = "LINEA_CINCO"
    LINEA_SEIS = "LINEA_SEIS"
    CONTROL_TARA = "CONTROL_TARA"
    CONTROL_PANZA = "CONTROL_PANZA"
    CONTROL_PANZA_ENTRADAS = "CONTROL_PANZA_ENTRADAS"
    ADMINISTRACION = "ADMINISTRACION"
    AREA_OPERARIOS = "AREA_OPERARIOS"
    CONTROL_LOTE = "CONTROL_LOTE"
    ESPECIES = "ESPECIES"
    LINEAS_OPERARIOS = "LINEAS_OPERARIOS"
    PLANIFICACION_TURNO = "PLANIFICACION_TURNO"
    DETALLE_PRODUCCION = "DETALLE_PRODUCCION"
    CONTROL_LOTE_SALIDAS = "CONTROL_LOTE_SALIDAS"
    CONTROL_MIGA = "CONTROL_MIGA"

class PermisoEnum(Enum):
    """Enum para los tipos de permisos"""
    READ = "read"
    WRITE = "write"


@dataclass
class Usuario:
    """Entidad Usuario para autenticación"""
    id_usuario: Optional[int] = None
    username: str = ""
    password_hash: str = ""
    id_rol: Optional[int] = None
    is_superuser: bool = False
    is_active: bool = True
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    rol: Optional["Rol"] = None
    turnos_asignados: List["UsuarioTurnoAsignado"] = None
    def __post_init__(self):
        """Inicializa listas vacías si son None"""
        if self.rol and self.rol.permisos_modulo is None:
             self.rol.permisos_modulo = []
        if self.lineas_asignadas is None: 
            self.lineas_asignadas = []
    
    def asignar_linea(self, linea: "UsuarioLineaAsignada") -> None:
        """Asigna una línea al usuario"""
        if self.lineas_asignadas is None:
            self.lineas_asignadas = []
        if self.turnos_asignados is None: # <-- Añadir esto
            self.turnos_asignados = []
        self.lineas_asignadas.append(linea)

    def desactivar(self) -> None:
        """Desactiva el usuario"""
        self.is_active = False

    def activar(self) -> None:
        """Activa el usuario"""
        self.is_active = True

    def asignar_rol(self, rol: "Rol") -> None:
        """Asigna un rol al usuario"""
        self.rol = rol
        self.id_rol = rol.id_rol

    def actualizar_ultimo_login(self) -> None:
        """Actualiza la fecha del último login"""
        self.last_login = datetime.now()

    def validar_datos_basicos(self) -> bool:
        """Valida que los datos básicos del usuario sean correctos"""
        return (
            bool(self.username.strip())
            and bool(self.password_hash.strip())
            and len(self.username) >= 3
        )


@dataclass
class Rol:
    """Entidad Rol para definir roles de usuario"""
    id_rol: Optional[int] = None
    nombre: str = ""
    descripcion: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    permisos_modulo: List["PermisoModulo"] = None

    def __post_init__(self):
        if self.permisos_modulo is None:
            self.permisos_modulo = []

    def desactivar(self) -> None:
        """Desactiva el rol"""
        self.is_active = False

    def activar(self) -> None:
        """Activa el rol"""
        self.is_active = True

    def agregar_permiso_modulo(self, permiso_modulo: "PermisoModulo") -> None:
        """Agrega un permiso de módulo al rol"""
        if self.permisos_modulo is None:
            self.permisos_modulo = []
        self.permisos_modulo.append(permiso_modulo)

    def tiene_permiso(self, modulo: ModuloEnum, permiso: PermisoEnum) -> bool:
        """Verifica si el rol tiene un permiso específico en un módulo"""
        if not self.permisos_modulo:
            return False
        
        for permiso_modulo in self.permisos_modulo:
            if (permiso_modulo.modulo == modulo and 
                permiso in permiso_modulo.permisos):
                return True
        return False

    def validar_datos_basicos(self) -> bool:
        """Valida que los datos básicos del rol sean correctos"""
        return (
            bool(self.nombre.strip())
            and len(self.nombre) >= 2
        )


@dataclass
class PermisoModulo:
    """Entidad que relaciona roles con módulos y sus permisos"""
    id_permiso_modulo: Optional[int] = None
    id_rol: int = 0
    modulo: ModuloEnum = ModuloEnum.CONFIGURACION
    permisos: List[PermisoEnum] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    rol: Optional[Rol] = None

    def __post_init__(self):
        if self.permisos is None:
            self.permisos = []

    def desactivar(self) -> None:
        """Desactiva el permiso del módulo"""
        self.is_active = False

    def activar(self) -> None:
        """Activa el permiso del módulo"""
        self.is_active = True

    def agregar_permiso(self, permiso: PermisoEnum) -> None:
        """Agrega un permiso al módulo"""
        if self.permisos is None:
            self.permisos = []
        if permiso not in self.permisos:
            self.permisos.append(permiso)

    def remover_permiso(self, permiso: PermisoEnum) -> None:
        """Remueve un permiso del módulo"""
        if self.permisos and permiso in self.permisos:
            self.permisos.remove(permiso)

    def tiene_permiso_lectura(self) -> bool:
        """Verifica si tiene permiso de lectura"""
        return PermisoEnum.READ in (self.permisos or [])

    def tiene_permiso_escritura(self) -> bool:
        """Verifica si tiene permiso de escritura"""
        return PermisoEnum.WRITE in (self.permisos or [])

    def validar_datos_basicos(self) -> bool:
        """Valida que los datos básicos del permiso sean correctos"""
        return (
            self.id_rol > 0
            and self.modulo is not None
            and self.permisos is not None
            and len(self.permisos) > 0
        )


@dataclass
class SesionUsuario:
    """Entidad para manejar sesiones de usuario"""
    id_sesion: Optional[int] = None
    id_usuario: int = 0
    token: str = ""
    refresh_token: Optional[str] = None
    fecha_inicio: Optional[datetime] = None
    fecha_expiracion: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    usuario: Optional[Usuario] = None

    def desactivar(self) -> None:
        """Desactiva la sesión"""
        self.is_active = False

    def activar(self) -> None:
        """Activa la sesión"""
        self.is_active = True

    def es_valida(self) -> bool:
        """Verifica si la sesión es válida"""
        if not self.is_active:
            return False
        
        if self.fecha_expiracion and datetime.now() > self.fecha_expiracion:
            return False
            
        return True

    def renovar_expiracion(self) -> None:
        """Renueva la fecha de expiración de la sesión"""
        from datetime import timedelta
        self.fecha_expiracion = datetime.now() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)

    def validar_datos_basicos(self) -> bool:
        """Valida que los datos básicos de la sesión sean correctos"""
        return (
            self.id_usuario > 0
            and bool(self.token.strip())
            and self.fecha_inicio is not None
            and self.fecha_expiracion is not None
        )

@dataclass
class UsuarioLineaAsignada:
    """Entidad para la asignación de líneas a usuarios"""
    id_usuario_linea: Optional[int] = None
    id_usuario: int = 0
    id_linea_externa: int = 0  # O str, si el ID externo es un string
    created_at: Optional[datetime] = None
    usuario: Optional["Usuario"] = None
    def validar_datos_basicos(self) -> bool:
        """Valida que los datos básicos sean correctos"""
        return self.id_usuario > 0 and self.id_linea_externa > 0

@dataclass
class LineaExterna:
    """
    Entidad de dominio que representa una Línea de Trabajo
    de la base de datos externa (principal).
    """
    id_linea: int
    nombre: str
    estado: str
    id_planta: Optional[int] = None

    def esta_activa(self) -> bool:
        """Verifica si la línea está activa"""
        return self.estado == "ACTIVO"
    
@dataclass
class TurnoExterno:
    """
    Entidad de dominio que representa un Turno de Trabajo
    de la base de datos externa (principal).
    """
    id_turno: int
    nombre: str
    estado: str

    def esta_activo(self) -> bool:
        return self.estado == "ACTIVO"

@dataclass
class UsuarioTurnoAsignado:
    """Entidad para la asignación de turnos a usuarios"""
    id_usuario_turno: Optional[int] = None
    id_usuario: int = 0
    id_turno_externo: int = 0
    created_at: Optional[datetime] = None
    usuario: Optional["Usuario"] = None