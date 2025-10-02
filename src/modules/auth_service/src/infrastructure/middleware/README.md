# Middleware de Autorización

Este middleware proporciona un sistema completo de autenticación y autorización basado en roles, módulos y permisos para el servicio de autenticación.

## Características

- **Autenticación JWT**: Validación de tokens JWT con verificación de expiración
- **Autorización basada en roles**: Control de acceso basado en roles de usuario
- **Permisos por módulo**: Sistema granular de permisos por módulo del sistema
- **Dependencias de FastAPI**: Integración nativa con el sistema de dependencias de FastAPI
- **Decoradores**: Decoradores para especificar permisos requeridos en rutas
- **Manejo de errores**: Excepciones personalizadas con códigos de estado HTTP apropiados

## Estructura del Sistema de Permisos

### Módulos Disponibles
- `PRODUCCION`: Módulo de producción
- `INVENTARIO`: Módulo de inventario
- `EMPLEADOS`: Módulo de empleados
- `PLANTA`: Módulo de planta
- `REPORTES`: Módulo de reportes
- `CONFIGURACION`: Módulo de configuración

### Tipos de Permisos
- `READ`: Permiso de lectura
- `WRITE`: Permiso de escritura

## Uso Básico

### 1. Dependencias de FastAPI

```python
from fastapi import APIRouter, Depends
from src.modules.auth_service.src.infrastructure.middleware import (
    get_current_user,
    get_optional_user,
    require_read_access,
    require_write_access,
    require_full_access,
    require_module_access
)
from src.modules.auth_service.src.domain.entities import ModuloEnum

router = APIRouter()

# Requiere autenticación básica
@router.get("/perfil")
async def obtener_perfil(usuario = Depends(get_current_user)):
    return {"username": usuario.username}

# Autenticación opcional
@router.get("/publico")
async def endpoint_publico(usuario = Depends(get_optional_user)):
    if usuario:
        return {"message": f"Hola {usuario.username}"}
    return {"message": "Hola anónimo"}

# Requiere permiso de lectura en INVENTARIO
@router.get("/inventario")
async def listar_inventario(usuario = Depends(require_read_access(ModuloEnum.INVENTARIO))):
    return {"productos": []}

# Requiere permiso de escritura en INVENTARIO
@router.post("/inventario")
async def crear_producto(usuario = Depends(require_write_access(ModuloEnum.INVENTARIO))):
    return {"message": "Producto creado"}

# Requiere acceso completo (lectura y escritura) en INVENTARIO
@router.put("/inventario/{id}")
async def actualizar_producto(id: int, usuario = Depends(require_full_access(ModuloEnum.INVENTARIO))):
    return {"message": f"Producto {id} actualizado"}

# Requiere acceso al módulo (cualquier permiso)
@router.get("/empleados")
async def listar_empleados(usuario = Depends(require_module_access(ModuloEnum.EMPLEADOS))):
    return {"empleados": []}
```

### 2. Decoradores

```python
from src.modules.auth_service.src.infrastructure.middleware import (
    require_permissions,
    require_module,
    require_read_permission,
    require_write_permission,
    require_full_access,
    public_endpoint,
    get_current_user
)
from src.modules.auth_service.src.domain.entities import ModuloEnum, PermisoEnum

# Decorador para permisos específicos
@router.get("/reportes")
@require_permissions(ModuloEnum.REPORTES, [PermisoEnum.READ, PermisoEnum.WRITE])
async def obtener_reportes(usuario = Depends(get_current_user)):
    return {"reportes": []}

# Decorador para permiso de lectura
@router.get("/configuracion")
@require_read_permission(ModuloEnum.CONFIGURACION)
async def obtener_configuracion(usuario = Depends(get_current_user)):
    return {"config": {}}

# Decorador para permiso de escritura
@router.post("/configuracion")
@require_write_permission(ModuloEnum.CONFIGURACION)
async def actualizar_configuracion(usuario = Depends(get_current_user)):
    return {"message": "Configuración actualizada"}

# Decorador para acceso completo
@router.delete("/configuracion/{id}")
@require_full_access(ModuloEnum.CONFIGURACION)
async def eliminar_configuracion(id: int, usuario = Depends(get_current_user)):
    return {"message": f"Configuración {id} eliminada"}

# Decorador para acceso al módulo
@router.get("/planta")
@require_module(ModuloEnum.PLANTA)
async def obtener_estado_planta(usuario = Depends(get_current_user)):
    return {"estado": "Operativa"}

# Endpoint público (sin autenticación)
@router.get("/info")
@public_endpoint
async def obtener_informacion():
    return {"version": "1.0.0"}
```

## Manejo de Errores

El middleware maneja automáticamente los siguientes errores:

### Códigos de Estado HTTP

- **401 Unauthorized**: Token faltante, inválido, expirado o sesión inválida
- **403 Forbidden**: Permisos insuficientes o usuario inactivo

### Excepciones Personalizadas

```python
from src.modules.auth_service.src.infrastructure.middleware import (
    TokenMissingException,      # 401: Token no proporcionado
    TokenInvalidException,      # 401: Token inválido
    TokenExpiredException,      # 401: Token expirado
    SessionInvalidException,    # 401: Sesión inválida
    UserInactiveException,      # 403: Usuario inactivo
    InsufficientPermissionsException  # 403: Permisos insuficientes
)
```

## Configuración Avanzada

### Crear Dependencias Personalizadas

```python
from src.modules.auth_service.src.infrastructure.middleware import auth_middleware
from src.modules.auth_service.src.domain.entities import ModuloEnum, PermisoEnum

# Dependencia personalizada para múltiples módulos
def require_admin_access():
    async def dependency(usuario = Depends(get_current_user)):
        # Verificar si tiene acceso a CONFIGURACION con permisos completos
        if not auth_middleware.verify_permissions(
            usuario, 
            ModuloEnum.CONFIGURACION, 
            [PermisoEnum.READ, PermisoEnum.WRITE]
        ):
            raise InsufficientPermissionsException("Acceso de administrador requerido")
        return usuario
    return dependency

@router.get("/admin/panel")
async def panel_admin(usuario = Depends(require_admin_access())):
    return {"message": "Panel de administración"}
```

### Validación Manual de Permisos

```python
from src.modules.auth_service.src.infrastructure.middleware import auth_middleware

@router.get("/custom-validation")
async def validacion_personalizada(usuario = Depends(get_current_user)):
    # Verificación manual de permisos
    tiene_inventario = auth_middleware.verify_permissions(
        usuario, 
        ModuloEnum.INVENTARIO, 
        [PermisoEnum.READ]
    )
    
    tiene_reportes = auth_middleware.verify_permissions(
        usuario, 
        ModuloEnum.REPORTES, 
        [PermisoEnum.READ]
    )
    
    if not (tiene_inventario or tiene_reportes):
        raise InsufficientPermissionsException(
            "Se requiere acceso a INVENTARIO o REPORTES"
        )
    
    return {"message": "Validación personalizada exitosa"}
```

## Utilidades JWT

```python
from src.modules.auth_service.src.infrastructure.middleware import JWTUtils

# Validar token manualmente
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
if JWTUtils.is_token_valid(token):
    user_id = JWTUtils.extract_user_id(token)
    username = JWTUtils.extract_username(token)
    expiration = JWTUtils.get_token_expiration(token)
```

## Mejores Prácticas

1. **Usar dependencias para validación automática**: Prefiere las dependencias de FastAPI sobre la validación manual
2. **Combinar decoradores y dependencias**: Los decoradores son útiles para documentación, las dependencias para lógica
3. **Endpoints públicos**: Marca explícitamente los endpoints públicos con `@public_endpoint`
4. **Principio de menor privilegio**: Asigna solo los permisos mínimos necesarios
5. **Manejo de errores**: Deja que el middleware maneje los errores automáticamente

## Integración con Otros Microservicios

Para usar este middleware en otros microservicios:

```python
# En otro microservicio
from src.modules.auth_service.src.infrastructure.middleware import (
    get_current_user,
    require_read_access,
    ModuloEnum
)

@router.get("/mi-endpoint")
async def mi_endpoint(usuario = Depends(require_read_access(ModuloEnum.INVENTARIO))):
    return {"message": "Acceso autorizado"}
```

## Estructura de Respuesta del Usuario

El objeto `Usuario` retornado por las dependencias incluye:

```python
{
    "id_usuario": 1,
    "username": "admin",
    "is_active": True,
    "rol": {
        "nombre": "admin",
        "permisos_modulo": [...]
    },
    "permisos_modulos": [
        {
            "nombre": "INVENTARIO",
            "ruta": "/inventario",
            "permisos": ["read", "write"]
        }
    ]
}
```
