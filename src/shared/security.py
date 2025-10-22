from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, Any

from src.modules.auth_service.src.infrastructure.api.routers.auth import get_auth_use_case
from src.modules.auth_service.src.application.use_cases.auth_use_cases import AuthUseCase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user_data(
    token: str = Depends(oauth2_scheme),
    auth_use_case: AuthUseCase = Depends(get_auth_use_case)
) -> Dict[str, Any]:
    """
    Dependencia de seguridad:
    1. Exige un token.
    2. Verifica el token (y la sesión en la BD) usando AuthUseCase.
    3. Devuelve el payload del usuario (incluyendo 'lineas') o lanza 401.
    """
    user_data = auth_use_case.verify_token(token)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o sesión expirada",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_data