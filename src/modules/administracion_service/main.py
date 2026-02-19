from fastapi import FastAPI

from src.modules.administracion_service.src.infrastructure.api.routers.detalle_produccion_router import router as detalle_produccion_router
from src.modules.administracion_service.src.infrastructure.api.routers.planning_turno_router import router as planning_turno_router
from src.modules.administracion_service.src.infrastructure.api.routers.planta_router import router as plantas_router
from src.modules.administracion_service.src.infrastructure.api.routers.lineas_router import router as lineas_router
from src.modules.administracion_service.src.infrastructure.api.routers.area_operarios_router import router as area_operarios_router
from src.modules.administracion_service.src.infrastructure.api.routers.control_lote_asiglinea_router import router as control_lote_asiglinea_router
from src.modules.administracion_service.src.infrastructure.api.routers.especies_router import router as especies_router
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
app.include_router(especies_router, prefix="/api/administracion/especies", tags=["Especies"])
app.include_router(lineas_router, prefix="/api/administracion/lineas", tags=["Lineas Operarios"])
app.include_router(plantas_router, prefix="/api/administracion/plantas", tags=["Plantas"])
app.include_router(planning_turno_router, prefix="/api/administracion/planif-turno", tags=["Planificación Turno"])
app.include_router(detalle_produccion_router, prefix="/api/administracion/detalle-prod", tags=["Detalle Producción"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "administracion_service"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8024)