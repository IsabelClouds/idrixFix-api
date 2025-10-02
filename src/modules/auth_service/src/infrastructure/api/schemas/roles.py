from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class RolBase(BaseModel):
    """Schema base para Rol"""
    nombre: str = Field(..., min_length=2, max_length=50)
    descripcion: Optional[str] = Field(None, max_length=500)


class RolCreate(RolBase):
    """Schema para crear Rol"""
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Supervisor",
                "descripcion": "Supervisor de planta con acceso limitado"
            }
        }


class RolUpdate(BaseModel):
    """Schema para actualizar Rol"""
    nombre: Optional[str] = Field(None, min_length=2, max_length=50)
    descripcion: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "descripcion": "Supervisor de planta con acceso ampliado"
            }
        }


class RolResponse(RolBase):
    """Schema para respuesta de Rol"""
    id_rol: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id_rol": 1,
                "nombre": "Administrador",
                "descripcion": "Acceso completo al sistema",
                "is_active": True,
                "created_at": "2024-01-01T08:00:00",
                "updated_at": "2024-01-01T08:00:00"
            }
        }


class RolWithPermisosResponse(RolResponse):
    """Schema para respuesta de Rol con permisos"""
    modulos: List[Dict[str, Any]]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id_rol": 1,
                "nombre": "Administrador",
                "descripcion": "Acceso completo al sistema",
                "is_active": True,
                "created_at": "2024-01-01T08:00:00",
                "updated_at": "2024-01-01T08:00:00",
                "modulos": [
                    {
                        "nombre": "PRODUCCION",
                        "ruta": "/produccion",
                        "permisos": ["read", "write"]
                    },
                    {
                        "nombre": "INVENTARIO",
                        "ruta": "/inventario",
                        "permisos": ["read", "write"]
                    }
                ]
            }
        }


class AsignPermisosRequest(BaseModel):
    """Schema para asignar permisos a un rol"""
    permisos: List[Dict[str, Any]] = Field(..., min_items=1)

    class Config:
        json_schema_extra = {
            "example": {
                "permisos": [
                    {
                        "modulo": "PRODUCCION",
                        "ruta": "/produccion",
                        "permisos": ["read", "write"]
                    },
                    {
                        "modulo": "INVENTARIO",
                        "ruta": "/inventario",
                        "permisos": ["read"]
                    }
                ]
            }
        }


class ModulosDisponiblesResponse(BaseModel):
    """Schema para módulos disponibles"""
    modulos: List[Dict[str, Any]]

    class Config:
        json_schema_extra = {
            "example": {
                "modulos": [
                    {
                        "nombre": "PRODUCCION",
                        "ruta": "/produccion",
                        "permisos_disponibles": ["read", "write"]
                    },
                    {
                        "nombre": "INVENTARIO",
                        "ruta": "/inventario",
                        "permisos_disponibles": ["read", "write"]
                    }
                ]
            }
        }
