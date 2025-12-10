from typing import List

from src.modules.administracion_service.src.application.ports.lineas import ILineaRepository
from src.modules.administracion_service.src.application.ports.planta import IPlantaRepository
from src.modules.administracion_service.src.infrastructure.api.schemas.linea import LineaCreate, LineaResponse, \
    LineaUpdate
from src.shared.exceptions import NotFoundError, AlreadyExistsError, ValidationError


class LineaUseCase:
    def __init__(self, lineas_repository: ILineaRepository, planta_repository: IPlantaRepository):
        self.lineas_repository = lineas_repository
        self.planta_repository = planta_repository

    def create_linea(self, data: LineaCreate) -> LineaResponse:
        if not data.line_nombre:
            raise ValidationError("El nombre no puede estar vacío")

        exists = self.lineas_repository.exists_by_nombre(data.line_nombre)
        if exists:
            raise AlreadyExistsError("Ya existe una linea con este nombre")

        linea = self.lineas_repository.create(data)
        planta = self.planta_repository.get_by_id(linea.line_planta)
        return LineaResponse(
            line_id=linea.line_id,
            line_nombre=linea.line_nombre,
            line_estado=linea.line_estado,
            line_feccre=linea.line_feccre,
            line_fecmod=linea.line_fecmod,
            line_planta=planta
        )

    def update_linea(self, data: LineaUpdate, id: int) -> LineaResponse:
        exists = self.lineas_repository.exists_by_id(id)
        if not exists:
            raise NotFoundError("Linea no encontrada")

        exists = self.lineas_repository.exists_by_nombre(data.line_nombre)
        if exists:
            raise AlreadyExistsError("Ya existe una linea con este nombre")

        linea = self.lineas_repository.update(data, id)
        planta = self.planta_repository.get_by_id(linea.line_planta)

        return LineaResponse(
            line_id=linea.line_id,
            line_nombre=linea.line_nombre,
            line_estado=linea.line_estado,
            line_feccre=linea.line_feccre,
            line_fecmod=linea.line_fecmod,
            line_planta=planta
        )

    def get_linea_by_id(self, id: int) -> LineaResponse:
        linea = self.lineas_repository.get_by_id(id)
        planta = self.planta_repository.get_by_id(linea.line_planta)
        if not linea:
            raise NotFoundError("No existe la linea")
        return LineaResponse(
            line_id=linea.line_id,
            line_nombre=linea.line_nombre,
            line_estado=linea.line_estado,
            line_feccre=linea.line_feccre,
            line_fecmod=linea.line_fecmod,
            line_planta=planta
        )

    def get_all_lineas(self) -> List[LineaResponse]:
        lineas = self.lineas_repository.get_all()
        lineas_response = []

        for linea in lineas:
            planta = self.planta_repository.get_by_id(linea.line_planta)
            linea_resp = LineaResponse(
                line_id=linea.line_id,
                line_nombre=linea.line_nombre,
                line_estado=linea.line_estado,
                line_feccre=linea.line_feccre,
                line_fecmod=linea.line_fecmod,
                line_planta=planta
            )
            lineas_response.append(linea_resp)

        return lineas_response

    def soft_delete_linea(self, id: int) -> bool:
        exists = self.lineas_repository.exists_by_id(id)
        if not exists:
            raise NotFoundError("Linea no encontrada")

        return self.lineas_repository.soft_delete(id)
