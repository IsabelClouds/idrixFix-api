from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError

from src.modules.lineas_entrada_salida_service.infrastructure.api.routers.control_tara_router import router as control_tara_router
from src.modules.lineas_entrada_salida_service.infrastructure.api.routers.lineas_salida_router import router as lineas_salida_router
from src.modules.lineas_entrada_salida_service.infrastructure.api.routers.lineas_entrada_router import router as lineas_entrada_router
from src.shared.common.responses import validation_error_response
from src.shared.exceptions import DomainError
from src.shared.common.exception_handlers import domain_exception_handler
from src.shared.config import settings
from src.shared.cors_config import configure_cors
import src.shared.models
from datetime import datetime

from src.modules.management_service.src.infrastructure.api.routers.movimientos_empleado import (
    router as router_movimientos,
)
from src.modules.auth_service.src.infrastructure.api.routers.auth import (
    router as auth_router,
)
from src.modules.auth_service.src.infrastructure.api.routers.usuarios import (
    router as usuarios_router,
)
from src.modules.auth_service.src.infrastructure.api.routers.roles import (
    router as roles_router,
)
from src.modules.auth_service.src.infrastructure.api.routers.lineas_asignadas_router import (
    router as lineas_asignadas_router,
)
from src.modules.auth_service.src.infrastructure.api.routers.turnos_asignados_router import (
    router as turnos_asignados_router,
)
from src.modules.management_service.src.infrastructure.api.routers.movimientos_empleado import (
    router as movimientos_empleado_router,
)
from src.modules.auth_service.src.infrastructure.api.routers.auditoria_logs_router import router as auditoria_logs
app = FastAPI(
    title="Administracion API Gateway -- CIESA",
    description="API Gateway que expone todos los servicios de manera unificada (modo monolítico para compatibilidad)",
    version="1.0.0",
)

# --- INICIO: CONFIGURACIÓN DE CORS ---
configure_cors(app, "API Gateway")
# --- FIN: CONFIGURACIÓN DE CORS ---


# Manejador global de excepciones de validación
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return validation_error_response(exc.errors())


# Manejador global de excepciones de dominio
@app.exception_handler(DomainError)
async def domain_exception_handler_app(request: Request, exc: DomainError):
    return await domain_exception_handler(request, exc)


# Servicio de empleados
app.include_router(router_movimientos, prefix="/api/movimientos/empleados", tags=["Movimientos empleados"])
app.include_router(auth_router, prefix="/api/auth", tags=["Autenticación"])
app.include_router(usuarios_router, prefix="/api/usuarios", tags=["Usuarios"])
app.include_router(roles_router, prefix="/api/roles", tags=["Roles"])
app.include_router(lineas_asignadas_router, prefix="/api/lineas-asignadas", tags=["Lineas Asignadas"])
app.include_router(turnos_asignados_router, prefix="/api/turnos-asignados", tags=["Turnos Asignados"])
app.include_router(movimientos_empleado_router, prefix="/api/movimientos-empleado", tags=["Movimientos Empleados"])
app.include_router(auditoria_logs, prefix="/api/auditoria", tags=["Auditoria de Registros"])
app.include_router(lineas_entrada_router, prefix="/api/lineas-entrada", tags=["Lineas Entrada"])
app.include_router(lineas_salida_router, prefix="/api/lineas-salida", tags=["Lineas Salida"])
app.include_router(control_tara_router, prefix="/api/control-tara", tags=["Control Tara"])

@app.get("/health")
async def health_check():
    """Endpoint de salud"""
    try:
        return {
            "status": "healthy",
            "mode": "monolithic_gateway",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e), "mode": "monolithic_gateway"}


@app.get("/health/detailed")
async def detailed_health_check():
    """Endpoint de salud con verificación de BD"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "mode": "monolithic_gateway",
        "checks": {"application": "healthy", "database": "unknown"},
    }

    try:
        # Intentar verificar la conexión a la base de datos
        from src.shared.base import get_db

        db = next(get_db())
        db.execute("SELECT 1")
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    return health_status


@app.get("/services")
async def get_services():
    """Endpoint que muestra los servicios disponibles"""
    return {
        "services": [
            {"name": "management_service", "port": 8001, "status": "available"},
        ],
        "mode": "monolithic_gateway",
        "description": "API Gateway que permite acceso unificado a todos los servicios",
    }
