from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.modules.auth_service.src.application.use_cases.audit_use_case import AuditUseCase
from src.shared.common.auditoria import get_audit_use_case
from src.modules.auth_service.src.application.use_cases.auth_use_cases import AuthUseCase
from src.modules.auth_service.src.infrastructure.api.schemas.auth import (
    LoginRequest,
    LoginResponse,
    TokenVerifyRequest,
    TokenVerifyResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    LogoutRequest,
    ChangePasswordRequest, UpdatePasswordRequest,
)
from src.modules.auth_service.src.infrastructure.db.repositories.usuario_repository import UsuarioRepository
from src.modules.auth_service.src.infrastructure.db.repositories.rol_repository import RolRepository
from src.modules.auth_service.src.infrastructure.db.repositories.permiso_modulo_repository import PermisoModuloRepository
from src.modules.auth_service.src.infrastructure.db.repositories.sesion_repository import SesionRepository
from src.modules.auth_service.src.application.use_cases.usuario_use_cases import UsuarioUseCase
from src.shared.common.responses import success_response, error_response
from sqlalchemy.orm import Session
from src.shared.base import get_auth_db

router = APIRouter()
security = HTTPBearer()


def get_auth_use_case(db: Session = Depends(get_auth_db)) -> AuthUseCase:
    """Dependency para obtener el caso de uso de autenticación"""
    return AuthUseCase(
        usuario_repository=UsuarioRepository(db),
        rol_repository=RolRepository(db),
        permiso_repository=PermisoModuloRepository(db),
        sesion_repository=SesionRepository(db),
    )


def get_usuario_use_case(db: Session = Depends(get_auth_db), audit_uc: AuditUseCase = Depends(get_audit_use_case)) -> UsuarioUseCase:
    """Dependency para obtener el caso de uso de usuarios"""
    return UsuarioUseCase(
        usuario_repository=UsuarioRepository(db),
        rol_repository=RolRepository(db),
        audit_use_case=audit_uc
    )


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_use_case: AuthUseCase = Depends(get_auth_use_case)
) -> int:
    """Dependency para obtener el ID del usuario actual desde el token"""
    try:
        user_info = auth_use_case.verify_token(credentials.credentials)
        if not user_info:
            raise HTTPException(status_code=401, detail="Token inválido o expirado")
        return user_info["user_id"]
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
def login(
    request: Request,
    login_data: LoginRequest,
    auth_use_case: AuthUseCase = Depends(get_auth_use_case)
):
    """Endpoint para autenticar usuario"""
    # Obtener información de la request
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    result = auth_use_case.login(login_data, ip_address, user_agent)
    return success_response(
        data=LoginResponse.model_validate(result).model_dump(mode="json"),
        message="Login exitoso"
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    logout_data: LogoutRequest,
    auth_use_case: AuthUseCase = Depends(get_auth_use_case)
):
    """Endpoint para cerrar sesión"""
    success = auth_use_case.logout(logout_data.token)
    if not success:
        return error_response(
            message="Token no encontrado",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return success_response(
        data={"logged_out": True},
        message="Sesión cerrada exitosamente"
    )


@router.post("/verify-token", response_model=TokenVerifyResponse, status_code=status.HTTP_200_OK)
def verify_token(
    token_data: TokenVerifyRequest,
    auth_use_case: AuthUseCase = Depends(get_auth_use_case)
):
    """Endpoint para verificar token"""
    user_info = auth_use_case.verify_token(token_data.token)
    if not user_info:
        return error_response(
            message="Token inválido o expirado",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    return success_response(
        data=TokenVerifyResponse.model_validate(user_info).model_dump(mode="json"),
        message="Token válido"
    )


@router.post("/refresh-token", response_model=RefreshTokenResponse, status_code=status.HTTP_200_OK)
def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_use_case: AuthUseCase = Depends(get_auth_use_case)
):
    """Endpoint para renovar token"""
    result = auth_use_case.refresh_token(refresh_data.token)
    if not result:
        return error_response(
            message="Token inválido o expirado",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    return success_response(
        data=RefreshTokenResponse.model_validate(result).model_dump(mode="json"),
        message="Token renovado exitosamente"
    )


@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    password_data: ChangePasswordRequest,
    current_user_id: int = Depends(get_current_user_id),
    usuario_use_case: UsuarioUseCase = Depends(get_usuario_use_case)
):
    """Endpoint para cambiar contraseña"""
    success = usuario_use_case.change_password(
        current_user_id,
        password_data.current_password,
        password_data.new_password
    )
    
    if not success:
        return error_response(
            message="Error al cambiar contraseña",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    return success_response(
        data={"password_changed": True},
        message="Contraseña cambiada exitosamente"
    )


@router.post("/logout-all", status_code=status.HTTP_200_OK)
def logout_all_sessions(
    current_user_id: int = Depends(get_current_user_id),
    auth_use_case: AuthUseCase = Depends(get_auth_use_case)
):
    """Endpoint para cerrar todas las sesiones del usuario"""
    success = auth_use_case.logout_all_sessions(current_user_id)
    if not success:
        return error_response(
            message="Error al cerrar sesiones",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    return success_response(
        data={"all_sessions_closed": True},
        message="Todas las sesiones han sido cerradas"
    )


@router.get("/me", response_model=TokenVerifyResponse, status_code=status.HTTP_200_OK)
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_use_case: AuthUseCase = Depends(get_auth_use_case)
):
    """Endpoint para obtener información del usuario actual"""
    user_info = auth_use_case.verify_token(credentials.credentials)
    if not user_info:
        return error_response(
            message="Token inválido o expirado",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    return success_response(
        data=TokenVerifyResponse.model_validate(user_info).model_dump(mode="json"),
        message="Información del usuario obtenida"
    )


@router.put("/{usuario_id}/update-password", status_code=status.HTTP_200_OK)
def change_password(
        usuario_id: int,
        password_data: UpdatePasswordRequest,
        usuario_use_case: UsuarioUseCase = Depends(get_usuario_use_case)
):
    """Endpoint para cambiar contraseña"""
    success = usuario_use_case.update_password(
        usuario_id,
        password_data.new_password
    )

    if not success:
        return error_response(
            message="Error al cambiar contraseña",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    return success_response(
        data={"password_changed": True},
        message="Contraseña cambiada exitosamente"
    )