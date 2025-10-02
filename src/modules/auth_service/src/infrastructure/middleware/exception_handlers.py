"""
Manejadores de excepciones para el middleware de autorización
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from .exceptions import (
    AuthorizationException,
    TokenMissingException,
    TokenInvalidException,
    TokenExpiredException,
    InsufficientPermissionsException,
    UserInactiveException,
    SessionInvalidException
)


async def authorization_exception_handler(request: Request, exc: AuthorizationException) -> JSONResponse:
    """Manejador para excepciones de autorización (403)"""
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "success": False,
            "message": exc.detail if isinstance(exc.detail, str) else exc.detail.get("message", "No autorizado")
        }
    )


async def token_missing_exception_handler(request: Request, exc: TokenMissingException) -> JSONResponse:
    """Manejador para token faltante (401)"""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "success": False,
            "message": exc.detail if isinstance(exc.detail, str) else exc.detail.get("message", "Token de autenticación requerido")
        },
        headers={"WWW-Authenticate": "Bearer"}
    )


async def token_invalid_exception_handler(request: Request, exc: TokenInvalidException) -> JSONResponse:
    """Manejador para token inválido (401)"""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "success": False,
            "message": exc.detail if isinstance(exc.detail, str) else exc.detail.get("message", "Token de autenticación inválido")
        },
        headers={"WWW-Authenticate": "Bearer"}
    )


async def token_expired_exception_handler(request: Request, exc: TokenExpiredException) -> JSONResponse:
    """Manejador para token expirado (401)"""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "success": False,
            "message": exc.detail if isinstance(exc.detail, str) else exc.detail.get("message", "Token de autenticación expirado")
        },
        headers={"WWW-Authenticate": "Bearer"}
    )


async def insufficient_permissions_exception_handler(request: Request, exc: InsufficientPermissionsException) -> JSONResponse:
    """Manejador para permisos insuficientes (403)"""
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "success": False,
            "message": exc.detail if isinstance(exc.detail, str) else exc.detail.get("message", "Permisos insuficientes")
        }
    )


async def user_inactive_exception_handler(request: Request, exc: UserInactiveException) -> JSONResponse:
    """Manejador para usuario inactivo (403)"""
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "success": False,
            "message": exc.detail if isinstance(exc.detail, str) else exc.detail.get("message", "Usuario inactivo")
        }
    )


async def session_invalid_exception_handler(request: Request, exc: SessionInvalidException) -> JSONResponse:
    """Manejador para sesión inválida (401)"""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "success": False,
            "message": exc.detail if isinstance(exc.detail, str) else exc.detail.get("message", "Sesión inválida o expirada")
        },
        headers={"WWW-Authenticate": "Bearer"}
    )


def register_auth_exception_handlers(app):
    """
    Registra todos los manejadores de excepciones del middleware de autorización
    
    Args:
        app: Instancia de FastAPI
    """
    app.add_exception_handler(AuthorizationException, authorization_exception_handler)
    app.add_exception_handler(TokenMissingException, token_missing_exception_handler)
    app.add_exception_handler(TokenInvalidException, token_invalid_exception_handler)
    app.add_exception_handler(TokenExpiredException, token_expired_exception_handler)
    app.add_exception_handler(InsufficientPermissionsException, insufficient_permissions_exception_handler)
    app.add_exception_handler(UserInactiveException, user_inactive_exception_handler)
    app.add_exception_handler(SessionInvalidException, session_invalid_exception_handler)
