from typing import Dict, Any, Optional, List, Tuple
from math import ceil
from src.modules.auth_service.src.application.ports.auditoria_log_repository import IAuditoriaLogRepository
from src.modules.auth_service.src.application.ports.usuarios import IUsuarioRepository
from src.modules.auth_service.src.infrastructure.api.schemas.usuarios import UsuarioResponse
from src.modules.auth_service.src.infrastructure.api.schemas.auditoria import AuditoriaLogFilters, AuditoriaLogPagination
from src.modules.auth_service.src.infrastructure.db.models import AuditoriaLogORM

class AuditUseCase:
    
    def __init__(
        self, 
        log_repository: IAuditoriaLogRepository,
        user_repository: IUsuarioRepository
    ):
        self.log_repository = log_repository
        self.user_repository = user_repository

    def _get_user_snapshot(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un snapshot JSON simple del usuario que realiza la acción."""
        try:
            # Usamos el repositorio de usuarios para obtener el objeto
            usuario = self.user_repository.get_by_id(user_id)
            if usuario:
                # Usamos el schema 'UsuarioResponse' para convertirlo a un JSON limpio
                return UsuarioResponse.model_validate(usuario).model_dump(mode="json")
        except Exception:
            return None # No fallar si el usuario no se encuentra

    def log_action(
        self,
        accion: str,
        user_id: int,
        modelo: str,
        entidad_id: str,
        datos_nuevos: Optional[Dict[str, Any]] = None,
        datos_anteriores: Optional[Dict[str, Any]] = None
    ):
        """
        Método principal para registrar una acción de auditoría.
        """
        # Obtenemos el snapshot del usuario
        user_snapshot = self._get_user_snapshot(user_id)
        
        log_data = {
            "modelo": modelo,
            "entidad_id": str(entidad_id),
            "accion": accion,
            "datos_anteriores": datos_anteriores,
            "datos_nuevos": datos_nuevos,
            "ejecutado_por_id": user_id,
            "ejecutado_por_json": user_snapshot
        }
        
        # Enviamos a la base de datos
        self.log_repository.create_log(log_data)

    def count_logs_by_filters(self, filters: AuditoriaLogFilters) -> int:
        """Obtiene el conteo total de logs según filtros."""
        return self.log_repository.count_by_filters(filters)

    def get_logs_paginated_by_filters(
        self, pagination_params: AuditoriaLogPagination
    ) -> Dict[str, Any]:
        """Obtiene logs paginados según filtros."""
        
        orm_list, total_records = self.log_repository.get_paginated_by_filters(
            filters=pagination_params, # Pasamos el objeto completo que incluye los filtros
            page=pagination_params.page,
            page_size=pagination_params.page_size
        )
        
        total_pages = ceil(total_records / pagination_params.page_size) if total_records > 0 else 0

        # Devolvemos un diccionario listo para el router
        # Incluyendo la lista de ORMs (el router mapeará a schemas)
        return {
            "total_records": total_records,
            "total_pages": total_pages,
            "page": pagination_params.page,
            "page_size": pagination_params.page_size,
            "data": orm_list, 
        }