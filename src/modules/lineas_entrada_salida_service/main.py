from fastapi import FastAPI

from src.modules.lineas_entrada_salida_service.infrastructure.api.routers.control_tara_router import router as control_tara_router
from src.modules.lineas_entrada_salida_service.infrastructure.api.routers.lineas_salida_router import router as lineas_salida_router
from src.modules.lineas_entrada_salida_service.infrastructure.api.routers.lineas_entrada_router import router as lineas_entrada_router
from src.shared.cors_config import configure_cors

app = FastAPI(
    title="Lineas Entrada-Salida API",
    description="Microservicio para la modificación de lineas de entrada-salida",
    version="1.0.0",
)

# Configurar CORS}
configure_cors(app, "Linea Entrada-Salida Service")

app.include_router(lineas_entrada_router, prefix="/api/lineas-entrada", tags=["Lineas Entrada"])
app.include_router(lineas_salida_router, prefix="/api/lineas-salida", tags=["Lineas Salida"])
app.include_router(control_tara_router, prefix="/api/control-tara", tags=["Control Tara"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "lineas_entrada_salida_service"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8003)