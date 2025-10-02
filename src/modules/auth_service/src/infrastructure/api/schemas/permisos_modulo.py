from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from src.modules.auth_service.src.domain.entities import ModuloEnum, PermisoEnum


class PermisoModuloBase(BaseModel):
    """Schema base para PermisoModulo"""
    id_rol: int = Field(..., gt=0)
    modulo: ModuloEnum
    permisos: List[PermisoEnum] = Field(..., min_items=1)
    ruta: str = Field(..., min_length=1, max_length=100)


class PermisoModuloCreate(PermisoModuloBase):
    """Schema para crear PermisoModulo"""
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_rol": 1,
                "modulo": "PRODUCCION",
                "permisos": ["read", "write"],
                "ruta": "/produccion"
            }
        }


class PermisoModuloUpdate(BaseModel):
    """Schema para actualizar PermisoModulo"""
    modulo: Optional[ModuloEnum] = None
    permisos: Optional[List[PermisoEnum]] = Field(None, min_items=1)
    ruta: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "permisos": ["read"],
                "ruta": "/produccion/reportes"
            }
        }


class PermisoModuloResponse(PermisoModuloBase):
    """Schema para respuesta de PermisoModulo"""
    id_permiso_modulo: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    rol: Optional[dict] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id_permiso_modulo": 1,
                "id_rol": 1,
                "modulo": "PRODUCCION",
                "permisos": ["read", "write"],
                "ruta": "/produccion",
                "is_active": True,
                "created_at": "2024-01-01T08:00:00",
                "updated_at": "2024-01-01T08:00:00",
                "rol": {
                    "id_rol": 1,
                    "nombre": "Administrador"
                }
            }
        }


class PermisoModuloListResponse(BaseModel):
    """Schema para lista de permisos de módulo"""
    permisos: List[PermisoModuloResponse]
    total: int

    class Config:
        json_schema_extra = {
            "example": {
                "permisos": [
                    {
                        "id_permiso_modulo": 1,
                        "id_rol": 1,
                        "modulo": "PRODUCCION",
                        "permisos": ["read", "write"],
                        "ruta": "/produccion",
                        "is_active": True,
                        "created_at": "2024-01-01T08:00:00",
                        "updated_at": "2024-01-01T08:00:00",
                        "rol": {
                            "id_rol": 1,
                            "nombre": "Administrador"
                        }
                    }
                ],
                "total": 1
            }
        }
