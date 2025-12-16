from typing import List, Dict, Any

from src.modules.administracion_service.src.application.ports.lineas import ILineaRepository
from src.modules.administracion_service.src.application.ports.planta import IPlantaRepository
from src.modules.administracion_service.src.infrastructure.api.schemas.linea import LineaCreate, LineaResponse, \
    LineaUpdate
from src.modules.auth_service.src.application.use_cases.audit_use_case import AuditUseCase
from src.shared.exceptions import NotFoundError, AlreadyExistsError, ValidationError


class LineaUseCase:
    def __init__(self, lineas_repository: ILineaRepository, planta_repository: IPlantaRepository, audit_use_case: AuditUseCase):
        self.lineas_repository = lineas_repository
        self.planta_repository = planta_repository
        self.audit_use_case = audit_use_case

    def create_linea(self, data: LineaCreate, user_data: Dict[str, Any]) -> LineaResponse:
        if not data.line_nombre:
            raise ValidationError("El nombre no puede estar vacío")

        exists = self.lineas_repository.exists_by_nombre(data.line_nombre)
        if exists:
            raise AlreadyExistsError("Ya existe una linea con este nombre")

        linea = self.lineas_repository.create(data)
        planta = self.planta_repository.get_by_id(linea.line_planta)

        response = LineaResponse(
            line_id=linea.line_id,
            line_nombre=linea.line_nombre,
            line_estado=linea.line_estado,
            line_feccre=linea.line_feccre,
            line_fecmod=linea.line_fecmod,
            line_planta=planta
        )
        self.audit_use_case.log_action(
            accion="CREATE",
            user_id=user_data.get("user_id"),
            modelo="fm_lineas_operarios",
            entidad_id=response.line_id,
            datos_nuevos=LineaResponse.model_validate(response).model_dump(mode="json")
        )

        return response

    def update_linea(self, data: LineaUpdate, id: int, user_data: Dict[str, Any]) -> LineaResponse:
        exists = self.lineas_repository.exists_by_id(id)
        if not exists:
            raise NotFoundError("Linea no encontrada")

        exists = self.lineas_repository.exists_by_nombre(data.line_nombre)
        if exists:
            raise AlreadyExistsError("Ya existe una linea con este nombre")

        linea_anterior = self.lineas_repository.get_by_id(id)

        linea = self.lineas_repository.update(data, id)
        planta = self.planta_repository.get_by_id(linea.line_planta)

        response = LineaResponse(
            line_id=linea.line_id,
            line_nombre=linea.line_nombre,
            line_estado=linea.line_estado,
            line_feccre=linea.line_feccre,
            line_fecmod=linea.line_fecmod,
            line_planta=planta
        )

        self.audit_use_case.log_action(
            accion="UPDATE",
            user_id=user_data.get("user_id"),
            modelo="fm_lineas_operarios",
            entidad_id=id,
            datos_nuevos=LineaResponse.model_validate(response).model_dump(mode="json"),
            datos_anteriores=LineaResponse.model_validate(linea_anterior).model_dump(mode="json")
        )

        return response

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

    def soft_delete_linea(self, id: int, user_data: Dict[str, Any]) -> bool:
        exists = self.lineas_repository.exists_by_id(id)
        if not exists:
            raise NotFoundError("Linea no encontrada")

        linea = self.lineas_repository.get_by_id(id)
        planta = self.planta_repository.get_by_id(linea.line_planta)

        linea_response = LineaResponse(
            line_id=linea.line_id,
            line_nombre=linea.line_nombre,
            line_estado=linea.line_estado,
            line_feccre=linea.line_feccre,
            line_fecmod=linea.line_fecmod,
            line_planta=planta
        )

        self.audit_use_case.log_action(
            accion="DELETE",
            user_id=user_data.get("user_id"),
            modelo="fm_lineas_operarios",
            entidad_id=id,
            datos_anteriores=LineaResponse.model_validate(linea_response).model_dump(mode="json")
        )

        return self.lineas_repository.soft_delete(id)
