"""
Middleware de autorización para verificar permisos y módulos
"""
from typing import Optional, List
from fastapi import Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.shared.base import get_auth_db
from src.modules.auth_service.src.infrastructure.db.models import Usuario, SesionUsuario
from src.modules.auth_service.src.domain.entities import ModuloEnum, PermisoEnum
from .exceptions import (
    TokenMissingException,
    TokenInvalidException,
    UserInactiveException,
    SessionInvalidException,
    InsufficientPermissionsException
)
from .jwt_utils import JWTUtils
from .decorators import get_endpoint_requirements


class AuthMiddleware:
    """Middleware para autenticación y autorización"""
    
    def __init__(self):
        self.security = HTTPBearer(auto_error=False)
    
    async def get_current_user(
        self,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
        db: Session = Depends(get_auth_db)
    ) -> Usuario:
        """
        Obtiene el usuario actual basado en el token JWT
        
        Args:
            credentials: Credenciales HTTP Bearer
            db: Sesión de base de datos
            
        Returns:
            Usuario autenticado
            
        Raises:
            TokenMissingException: Si no se proporciona token
            TokenInvalidException: Si el token es inválido
            UserInactiveException: Si el usuario está inactivo
            SessionInvalidException: Si la sesión es inválida
        """
        if not credentials:
            raise TokenMissingException()
        
        # Validar y decodificar token
        user_id = JWTUtils.extract_user_id(credentials.credentials)
        session_id = JWTUtils.extract_session_id(credentials.credentials)
        
        # Buscar usuario en base de datos
        usuario = db.query(Usuario).filter(
            Usuario.id_usuario == user_id,
            Usuario.deleted_at.is_(None)
        ).first()
        
        if not usuario:
            raise TokenInvalidException("Usuario no encontrado")
        
        if not usuario.is_active:
            raise UserInactiveException()
        
        # Validar sesión si está presente en el token
        if session_id:
            sesion = db.query(SesionUsuario).filter(
                SesionUsuario.id_sesion == session_id,
                SesionUsuario.id_usuario == user_id,
                SesionUsuario.token == credentials.credentials,
                SesionUsuario.is_active == True,
                SesionUsuario.deleted_at.is_(None)
            ).first()
            
            if not sesion:
                raise SessionInvalidException()
            
            # Verificar si la sesión es válida manualmente
            from datetime import datetime
            if (not sesion.is_active or 
                sesion.deleted_at is not None or
                (sesion.fecha_expiracion and datetime.now() > sesion.fecha_expiracion)):
                raise SessionInvalidException()
        
        return usuario
    
    async def get_optional_user(
        self,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
        db: Session = Depends(get_auth_db)
    ) -> Optional[Usuario]:
        """
        Obtiene el usuario actual si está autenticado, None en caso contrario
        
        Args:
            credentials: Credenciales HTTP Bearer
            db: Sesión de base de datos
            
        Returns:
            Usuario autenticado o None
        """
        try:
            return await self.get_current_user(credentials, db)
        except (TokenMissingException, TokenInvalidException, UserInactiveException, SessionInvalidException):
            return None
    
    def verify_permissions(
        self,
        usuario: Usuario,
        required_module: Optional[ModuloEnum] = None,
        required_permissions: Optional[List[PermisoEnum]] = None
    ) -> bool:
        """
        Verifica si el usuario tiene los permisos requeridos
        
        Args:
            usuario: Usuario a verificar
            required_module: Módulo requerido
            required_permissions: Lista de permisos requeridos
            
        Returns:
            True si tiene los permisos, False en caso contrario
        """
        if not required_module:
            return True  # Sin requerimientos específicos
        
        if not usuario.rol or not usuario.rol.is_active:
            return False
        
        # Buscar el módulo en los permisos del usuario
        modulos_usuario = usuario.permisos_modulos
        
        for modulo_info in modulos_usuario:
            if modulo_info["nombre"] == required_module.value:
                # Si no se requieren permisos específicos, solo acceso al módulo
                if not required_permissions:
                    return True
                
                # Verificar permisos específicos
                permisos_usuario = modulo_info.get("permisos", [])
                for permiso_requerido in required_permissions:
                    if permiso_requerido.value not in permisos_usuario:
                        return False
                
                return True
        
        return False
    
    async def require_authentication(
        self,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
        db: Session = Depends(get_auth_db)
    ) -> Usuario:
        """
        Dependencia que requiere autenticación
        
        Args:
            credentials: Credenciales HTTP Bearer
            db: Sesión de base de datos
            
        Returns:
            Usuario autenticado
        """
        return await self.get_current_user(credentials, db)
    
    async def require_permissions_dependency(
        self,
        required_module: ModuloEnum,
        required_permissions: List[PermisoEnum]
    ):
        """
        Crea una dependencia que requiere permisos específicos
        
        Args:
            required_module: Módulo requerido
            required_permissions: Lista de permisos requeridos
            
        Returns:
            Función de dependencia
        """
        async def dependency(
            usuario: Usuario = Depends(self.require_authentication)
        ) -> Usuario:
            if not self.verify_permissions(usuario, required_module, required_permissions):
                raise InsufficientPermissionsException(
                    modulo=required_module.value,
                    permiso=", ".join([p.value for p in required_permissions])
                )
            return usuario
        
        return dependency
    
    def create_permission_dependency(
        self,
        modulo: ModuloEnum,
        permisos: List[PermisoEnum] = None
    ):
        """
        Crea una dependencia de FastAPI para verificar permisos
        
        Args:
            modulo: Módulo requerido
            permisos: Lista de permisos requeridos
            
        Returns:
            Dependencia de FastAPI
        """
        async def permission_dependency(
            usuario: Usuario = Depends(self.require_authentication)
        ) -> Usuario:
            if not self.verify_permissions(usuario, modulo, permisos):
                raise InsufficientPermissionsException(
                    modulo=modulo.value,
                    permiso=", ".join([p.value for p in permisos]) if permisos else None
                )
            return usuario
        
        return permission_dependency


# Instancia global del middleware
auth_middleware = AuthMiddleware()


# Dependencias comunes
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_auth_db)
) -> Usuario:
    """Dependencia para obtener el usuario actual"""
    return await auth_middleware.get_current_user(credentials, db)


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_auth_db)
) -> Optional[Usuario]:
    """Dependencia para obtener el usuario actual opcional"""
    return await auth_middleware.get_optional_user(credentials, db)


def require_module_access(modulo: ModuloEnum):
    """Crea dependencia que requiere acceso a un módulo específico"""
    return auth_middleware.create_permission_dependency(modulo)


def require_read_access(modulo: ModuloEnum):
    """Crea dependencia que requiere permiso de lectura en un módulo"""
    return auth_middleware.create_permission_dependency(modulo, [PermisoEnum.READ])


def require_write_access(modulo: ModuloEnum):
    """Crea dependencia que requiere permiso de escritura en un módulo"""
    return auth_middleware.create_permission_dependency(modulo, [PermisoEnum.WRITE])


def require_full_access(modulo: ModuloEnum):
    """Crea dependencia que requiere acceso completo (lectura y escritura) a un módulo"""
    return auth_middleware.create_permission_dependency(
        modulo, 
        [PermisoEnum.READ, PermisoEnum.WRITE]
    )
