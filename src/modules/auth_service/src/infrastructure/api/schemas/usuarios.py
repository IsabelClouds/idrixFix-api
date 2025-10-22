from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from src.modules.auth_service.src.infrastructure.api.schemas.roles import RolResponse


class UsuarioBase(BaseModel):
    """Schema base para Usuario"""
    username: str = Field(..., min_length=3, max_length=50)
    id_rol: Optional[int] = None


class UsuarioCreate(UsuarioBase):
    """Schema para crear Usuario"""
    password: str = Field(..., min_length=8)
    password_hash: Optional[str] = None  # Se genera automáticamente

    class Config:
        json_schema_extra = {
            "example": {
                "username": "jperez",
                "password": "Password123!",
                "id_rol": 2
            }
        }


class UsuarioUpdate(BaseModel):
    """Schema para actualizar Usuario"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    id_rol: Optional[int] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)
    password_hash: Optional[str] = None  # Se genera automáticamente

    class Config:
        json_schema_extra = {
            "example": {
                "username": "jperez2",
                "id_rol": 3
            }
        }


class UsuarioResponse(UsuarioBase):
    """Schema para respuesta de Usuario con permisos por módulo"""
    id_usuario: int
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    rol: Optional[RolResponse] = None
    permisos_modulos: List[Dict[str, Any]] = []
    lineas_asignadas: List[LineaAsignadaResponse] = []

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id_usuario": 1,
                "username": "jperez",
                "id_rol": 2,
                "is_active": True,
                "last_login": "2024-01-01T10:30:00",
                "created_at": "2024-01-01T08:00:00",
                "updated_at": "2024-01-01T10:30:00",
                "rol": {
                    "id_rol": 2,
                    "nombre": "Supervisor",
                    "descripcion": "Supervisor de planta",
                    "is_active": True,
                    "created_at": "2024-01-01T08:00:00",
                    "updated_at": "2024-01-01T08:00:00"
                },
                "permisos_modulos": [
                    {
                        "nombre": "PRODUCCION",
                        "permisos": ["read", "write"]
                    },
                    {
                        "nombre": "INVENTARIO",
                        "permisos": ["read"]
                    }
                ],
                "lineas_asignadas": [
                    {"id_usuario_linea": 1, "id_usuario": 1, "id_linea_externa": 101, "created_at": "2024-01-01T08:00:00"},
                    {"id_usuario_linea": 2, "id_usuario": 1, "id_linea_externa": 105, "created_at": "2024-01-01T08:00:00"}
                ]
            }
        }

class LineaAsignadaBase(BaseModel):
    id_linea_externa: int = Field(..., gt=0, description="ID de la línea en la DB externa")

class LineaAsignadaCreate(LineaAsignadaBase):
    pass

class LineaAsignadaResponse(LineaAsignadaBase):
    id_usuario_linea: int
    id_usuario: int
    created_at: datetime

    class Config:
        from_attributes = True