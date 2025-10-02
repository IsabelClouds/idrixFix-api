"""
Middleware de autorización para el servicio de autenticación
"""

from .auth_middleware import (
    AuthMiddleware,
    auth_middleware,
    get_current_user,
    get_optional_user,
    require_module_access,
    require_read_access,
    require_write_access,
    require_full_access
)

from .decorators import (
    require_permissions,
    require_module,
    require_read_permission,
    require_write_permission,
    require_full_access as require_full_access_decorator,
    public_endpoint,
    get_endpoint_requirements
)

from .exceptions import (
    AuthorizationException,
    TokenMissingException,
    TokenInvalidException,
    TokenExpiredException,
    InsufficientPermissionsException,
    UserInactiveException,
    SessionInvalidException
)

from .jwt_utils import JWTUtils

from .exception_handlers import register_auth_exception_handlers

__all__ = [
    # Middleware principal
    'AuthMiddleware',
    'auth_middleware',
    
    # Dependencias de FastAPI
    'get_current_user',
    'get_optional_user',
    'require_module_access',
    'require_read_access',
    'require_write_access',
    'require_full_access',
    
    # Decoradores
    'require_permissions',
    'require_module',
    'require_read_permission',
    'require_write_permission',
    'require_full_access_decorator',
    'public_endpoint',
    'get_endpoint_requirements',
    
    # Excepciones
    'AuthorizationException',
    'TokenMissingException',
    'TokenInvalidException',
    'TokenExpiredException',
    'InsufficientPermissionsException',
    'UserInactiveException',
    'SessionInvalidException',
    
    # Utilidades JWT
    'JWTUtils',
    
    # Manejadores de excepciones
    'register_auth_exception_handlers'
]
