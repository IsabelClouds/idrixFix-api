import os
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from src.shared.common.responses import validation_error_response
from src.shared.cors_config import configure_cors
import src.shared.models
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
from src.shared.common.exception_handlers import domain_exception_handler
from src.shared.exceptions import DomainError

app = FastAPI(
    title="Auth Service API",
    description="Microservicio para la gestión de autenticación, usuarios, roles y permisos",
    version="1.0.0",
)

# Configurar CORS
configure_cors(app, "Auth Service")


# Manejador global de excepciones de validación
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return validation_error_response(exc.errors())


# Manejador global de excepciones de dominio
app.add_exception_handler(DomainError, domain_exception_handler)

# Manejador de excepciones de autorización
from src.modules.auth_service.src.infrastructure.middleware import register_auth_exception_handlers
register_auth_exception_handlers(app)

# Routers del servicio de autenticación
app.include_router(auth_router, prefix="/api/auth", tags=["Autenticación"])
app.include_router(usuarios_router, prefix="/api/usuarios", tags=["Usuarios"])
app.include_router(roles_router, prefix="/api/roles", tags=["Roles"])
app.include_router(lineas_asignadas_router, prefix="/api/lineas-asignadas", tags=["Lineas Asignadas"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "auth_service"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8022)
