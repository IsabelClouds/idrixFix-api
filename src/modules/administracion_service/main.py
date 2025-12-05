from fastapi import FastAPI

from src.modules.administracion_service.src.infrastructure.api.routers.area_operarios_router import router as area_operarios_router
from src.modules.administracion_service.src.infrastructure.api.routers.control_lote_asiglinea_router import router as control_lote_asiglinea_router
from src.shared.cors_config import configure_cors

app = FastAPI(
    title="Administración API",
    description="Microservicio para administración general",
    version="1.0.0",
)

# Configurar CORS
configure_cors(app, "Administración Service")

app.include_router(area_operarios_router, prefix="/api/administracion/area-operarios", tags=["Area Operarios"])
app.include_router(control_lote_asiglinea_router, prefix="/api/administracion/control-lote", tags=["Control Lote"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "administracion_service"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8004)