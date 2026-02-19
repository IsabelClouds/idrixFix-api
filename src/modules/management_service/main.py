from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from src.shared.common.responses import validation_error_response
from src.shared.cors_config import configure_cors
import src.shared.models
from src.modules.management_service.src.infrastructure.api.routers.movimientos_empleado import (
    router as movimientos_empleado_router,
)
from src.shared.common.exception_handlers import domain_exception_handler
from src.shared.exceptions import DomainError

app = FastAPI(
    title="Servicio de Administracion - API",
    description="Microservicio para la gestión modelos",
    version="1.0.0",
)

# Configurar CORS
configure_cors(app, "Management Service")


# Manejador global de excepciones de validación
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return validation_error_response(exc.errors())


# Manejador global de excepciones de dominio
app.add_exception_handler(DomainError, domain_exception_handler)


# Routers del servicio de management
app.include_router(
    movimientos_empleado_router, prefix="/api/movimientos-empleado", tags=["Movimientos Empleados"]
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "management_service"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8021)
