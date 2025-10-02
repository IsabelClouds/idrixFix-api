from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SesionBase(BaseModel):
    """Schema base para SesionUsuario"""
    id_usuario: int = Field(..., gt=0)
    token: str = Field(..., min_length=10)
    refresh_token: Optional[str] = None
    fecha_inicio: datetime
    fecha_expiracion: datetime
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = None


class SesionCreate(SesionBase):
    """Schema para crear SesionUsuario"""
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_usuario": 1,
                "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh_token": "refresh_token_here",
                "fecha_inicio": "2024-01-01T10:00:00",
                "fecha_expiracion": "2024-01-01T11:00:00",
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        }


class SesionResponse(SesionBase):
    """Schema para respuesta de SesionUsuario"""
    id_sesion: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    usuario: Optional[dict] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id_sesion": 1,
                "id_usuario": 1,
                "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh_token": "refresh_token_here",
                "fecha_inicio": "2024-01-01T10:00:00",
                "fecha_expiracion": "2024-01-01T11:00:00",
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "is_active": True,
                "created_at": "2024-01-01T10:00:00",
                "updated_at": "2024-01-01T10:00:00",
                "usuario": {
                    "id_usuario": 1,
                    "username": "admin",
                }
            }
        }


class SesionListResponse(BaseModel):
    """Schema para lista de sesiones"""
    sesiones: list[SesionResponse]
    total: int

    class Config:
        json_schema_extra = {
            "example": {
                "sesiones": [
                    {
                        "id_sesion": 1,
                        "id_usuario": 1,
                        "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "fecha_inicio": "2024-01-01T10:00:00",
                        "fecha_expiracion": "2024-01-01T11:00:00",
                        "is_active": True,
                        "usuario": {
                            "username": "admin"
                        }
                    }
                ],
                "total": 1
            }
        }


class SesionStatsResponse(BaseModel):
    """Schema para estadísticas de sesiones"""
    total_sesiones: int
    sesiones_activas: int
    sesiones_expiradas: int
    usuarios_conectados: int

    class Config:
        json_schema_extra = {
            "example": {
                "total_sesiones": 150,
                "sesiones_activas": 25,
                "sesiones_expiradas": 125,
                "usuarios_conectados": 20
            }
        }
