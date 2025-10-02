"""
Decoradores para especificar permisos requeridos en rutas
"""
from functools import wraps
from typing import List, Union, Callable, Any
from src.modules.auth_service.src.domain.entities import ModuloEnum, PermisoEnum


def require_permissions(
    modulo: Union[ModuloEnum, str],
    permisos: Union[List[PermisoEnum], List[str], PermisoEnum, str]
):
    """
    Decorador para especificar los permisos requeridos en una ruta
    
    Args:
        modulo: Módulo requerido (ModuloEnum o string)
        permisos: Permisos requeridos (lista de PermisoEnum/string o un solo permiso)
    
    Usage:
        @require_permissions(ModuloEnum.INVENTARIO, [PermisoEnum.READ, PermisoEnum.WRITE])
        @require_permissions("INVENTARIO", ["read", "write"])
        @require_permissions(ModuloEnum.EMPLEADOS, PermisoEnum.READ)
    """
    def decorator(func: Callable) -> Callable:
        # Normalizar módulo
        if isinstance(modulo, str):
            try:
                normalized_modulo = ModuloEnum(modulo)
            except ValueError:
                raise ValueError(f"Módulo inválido: {modulo}")
        else:
            normalized_modulo = modulo
        
        # Normalizar permisos
        if isinstance(permisos, (str, PermisoEnum)):
            permisos_list = [permisos]
        else:
            permisos_list = permisos
        
        normalized_permisos = []
        for permiso in permisos_list:
            if isinstance(permiso, str):
                try:
                    normalized_permisos.append(PermisoEnum(permiso))
                except ValueError:
                    raise ValueError(f"Permiso inválido: {permiso}")
            else:
                normalized_permisos.append(permiso)
        
        # Agregar metadatos al función
        func._required_module = normalized_modulo
        func._required_permissions = normalized_permisos
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Verificar si la función es asíncrona
            import asyncio
            if asyncio.iscoroutinefunction(func):
                async def async_wrapper():
                    return await func(*args, **kwargs)
                return async_wrapper()
            else:
                return func(*args, **kwargs)
        
        # Preservar metadatos en el wrapper
        wrapper._required_module = normalized_modulo
        wrapper._required_permissions = normalized_permisos
        
        return wrapper
    
    return decorator


def require_module(modulo: Union[ModuloEnum, str]):
    """
    Decorador para especificar solo el módulo requerido (cualquier permiso)
    
    Args:
        modulo: Módulo requerido (ModuloEnum o string)
    
    Usage:
        @require_module(ModuloEnum.INVENTARIO)
        @require_module("INVENTARIO")
    """
    def decorator(func: Callable) -> Callable:
        # Normalizar módulo
        if isinstance(modulo, str):
            try:
                normalized_modulo = ModuloEnum(modulo)
            except ValueError:
                raise ValueError(f"Módulo inválido: {modulo}")
        else:
            normalized_modulo = modulo
        
        # Agregar metadatos al función
        func._required_module = normalized_modulo
        func._required_permissions = []  # Sin permisos específicos
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Verificar si la función es asíncrona
            import asyncio
            if asyncio.iscoroutinefunction(func):
                async def async_wrapper():
                    return await func(*args, **kwargs)
                return async_wrapper()
            else:
                return func(*args, **kwargs)
        
        # Preservar metadatos en el wrapper
        wrapper._required_module = normalized_modulo
        wrapper._required_permissions = []
        
        return wrapper
    
    return decorator


def require_read_permission(modulo: Union[ModuloEnum, str]):
    """
    Decorador para requerir permiso de lectura en un módulo
    
    Args:
        modulo: Módulo requerido (ModuloEnum o string)
    
    Usage:
        @require_read_permission(ModuloEnum.INVENTARIO)
        @require_read_permission("INVENTARIO")
    """
    return require_permissions(modulo, PermisoEnum.READ)


def require_write_permission(modulo: Union[ModuloEnum, str]):
    """
    Decorador para requerir permiso de escritura en un módulo
    
    Args:
        modulo: Módulo requerido (ModuloEnum o string)
    
    Usage:
        @require_write_permission(ModuloEnum.INVENTARIO)
        @require_write_permission("INVENTARIO")
    """
    return require_permissions(modulo, PermisoEnum.WRITE)


def require_full_access(modulo: Union[ModuloEnum, str]):
    """
    Decorador para requerir acceso completo (lectura y escritura) en un módulo
    
    Args:
        modulo: Módulo requerido (ModuloEnum o string)
    
    Usage:
        @require_full_access(ModuloEnum.INVENTARIO)
        @require_full_access("INVENTARIO")
    """
    return require_permissions(modulo, [PermisoEnum.READ, PermisoEnum.WRITE])


def public_endpoint(func: Callable) -> Callable:
    """
    Decorador para marcar un endpoint como público (sin autenticación requerida)
    
    Usage:
        @public_endpoint
        async def login():
            pass
    """
    func._is_public = True
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Verificar si la función es asíncrona
        import asyncio
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper():
                return await func(*args, **kwargs)
            return async_wrapper()
        else:
            return func(*args, **kwargs)
    
    wrapper._is_public = True
    return wrapper


def get_endpoint_requirements(func: Callable) -> dict:
    """
    Obtiene los requerimientos de permisos de un endpoint
    
    Args:
        func: Función del endpoint
        
    Returns:
        Dict con los requerimientos del endpoint
    """
    return {
        'is_public': getattr(func, '_is_public', False),
        'required_module': getattr(func, '_required_module', None),
        'required_permissions': getattr(func, '_required_permissions', [])
    }
