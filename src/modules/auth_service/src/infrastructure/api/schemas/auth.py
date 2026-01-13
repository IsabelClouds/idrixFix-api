from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class LoginRequest(BaseModel):
    """Schema para solicitud de login"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "Admin123!"
            }
        }


class LoginResponse(BaseModel):
    """Schema para respuesta de login"""
    user_id: int
    username: str
    is_superuser: bool
    token: str
    expires_at: str
    rol: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "username": "admin",
                "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "expires_at": "2024-01-01T12:00:00",
                "rol": {
                    "nombre": "Administrador",
                    "modulos": [
                        {
                            "nombre": "PRODUCCION",
                            "permisos": ["read", "write"]
                        },
                        {
                            "nombre": "INVENTARIO",
                            "permisos": ["read"]
                        }
                    ]
                }
            }
        }


class TokenVerifyRequest(BaseModel):
    """Schema para verificación de token"""
    token: str = Field(..., min_length=10)


class TokenVerifyResponse(BaseModel):
    """Schema para respuesta de verificación de token"""
    user_id: int
    is_superuser: bool
    username: str
    rol: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "username": "admin",
                "rol": {
                    "id": 1,
                    "nombre": "Administrador",
                    "modulos": [
                        {
                            "nombre": "PRODUCCION",
                            "permisos": ["read", "write"]
                        }
                    ]
                }
            }
        }


class RefreshTokenRequest(BaseModel):
    """Schema para renovación de token"""
    token: str = Field(..., min_length=10)


class RefreshTokenResponse(BaseModel):
    """Schema para respuesta de renovación de token"""
    token: str
    expires_at: str
    user: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "expires_at": "2024-01-01T12:00:00",
                "user": {
                    "user_id": 1,
                    "username": "admin"
                }
            }
        }


class LogoutRequest(BaseModel):
    """Schema para solicitud de logout"""
    token: str = Field(..., min_length=10)


class ChangePasswordRequest(BaseModel):
    """Schema para cambio de contraseña"""
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)

    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "OldPassword123!",
                "new_password": "NewPassword123!"
            }
        }

class UpdatePasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=8)
