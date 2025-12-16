from math import ceil
from typing import Optional, Dict, Any

from src.modules.administracion_service.src.application.ports.detalle_produccion import IDetalleProduccionRepository
from src.modules.administracion_service.src.domain.entities import DetalleProduccion
from src.modules.administracion_service.src.infrastructure.api.schemas.detalle_produccion import (
    DetalleProduccionPagination, DetalleProduccionUpdate, DetalleProduccionResponse
)
from src.modules.auth_service.src.application.use_cases.audit_use_case import AuditUseCase
from src.shared.exceptions import NotFoundError

class DetalleProduccionUseCase:
    def __init__(self, repo: IDetalleProduccionRepository, audit_use_case: AuditUseCase):
        self.repo = repo
        self.audit_use_case = audit_use_case

    def get_paginated_by_filters(self, pagination: DetalleProduccionPagination):
        data, total_records = self.repo.get_paginated_by_filters(pagination)

        total_pages = ceil(total_records / pagination.page_size) if total_records > 0 else 0

        return {
            "total_records": total_records,
            "total_pages": total_pages,
            "page": pagination.page,
            "page_size": pagination.page_size,
            "data": data
        }

    def get_by_id(self, id: int) -> Optional[DetalleProduccion]:
        record = self.repo.get_by_id(id)
        if not record:
            raise NotFoundError("El registro no existe")
        return record


    def update(self, id: int, data: DetalleProduccionUpdate, user_data: Dict[str, Any]) -> DetalleProduccion:
        if not self.repo.exists_by_id(id):
            raise NotFoundError("No existe el registro")

        detalle = self.repo.get_by_id(id)

        updated_detalle = self.repo.update(id, data)

        self.audit_use_case.log_action(
            accion="UPDATE",
            user_id=user_data.get("user_id"),
            modelo="fm_detalle_produccion",
            entidad_id=id,
            datos_nuevos=DetalleProduccionResponse.model_validate(updated_detalle).model_dump(mode="json"),
            datos_anteriores=DetalleProduccionResponse.model_validate(detalle).model_dump(mode="json")
        )

        return updated_detalle

    def remove(self, id: int, user_data: Dict[str, Any]) -> bool:
        if not self.repo.exists_by_id(id):
            raise NotFoundError("No existe el registro")

        detalle = self.repo.get_by_id(id)

        self.audit_use_case.log_action(
            accion="DELETE",
            user_id=user_data.get("user_id"),
            modelo="fm_detalle_produccion",
            entidad_id=id,
            datos_anteriores=DetalleProduccionResponse.model_validate(detalle).model_dump(mode="json")
        )

        return self.repo.remove(id)
