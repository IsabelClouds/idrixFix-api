"""
Excepciones personalizadas para el middleware de autorización
"""
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse


class AuthorizationException(HTTPException):
    """Excepción base para errores de autorización"""
    def __init__(self, detail: str = "No autorizado"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class TokenMissingException(HTTPException):
    """Excepción cuando no se proporciona token de autenticación"""
    def __init__(self, detail: str = "Token de autenticación requerido"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class TokenInvalidException(HTTPException):
    """Excepción cuando el token es inválido"""
    def __init__(self, detail: str = "Token de autenticación inválido"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class TokenExpiredException(HTTPException):
    """Excepción cuando el token ha expirado"""
    def __init__(self, detail: str = "Token de autenticación expirado"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class InsufficientPermissionsException(AuthorizationException):
    """Excepción cuando el usuario no tiene permisos suficientes"""
    def __init__(self, modulo: str = None, permiso: str = None):
        if modulo and permiso:
            detail = f"Permisos insuficientes. Se requiere permiso '{permiso}' en el módulo '{modulo}'"
        elif modulo:
            detail = f"Acceso denegado al módulo '{modulo}'"
        else:
            detail = "Permisos insuficientes para realizar esta acción"
        
        super().__init__(detail=detail)


class UserInactiveException(AuthorizationException):
    """Excepción cuando el usuario está inactivo"""
    def __init__(self, detail: str = "Usuario inactivo"):
        super().__init__(detail=detail)


class SessionInvalidException(HTTPException):
    """Excepción cuando la sesión es inválida"""
    def __init__(self, detail: str = "Sesión inválida o expirada"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )
