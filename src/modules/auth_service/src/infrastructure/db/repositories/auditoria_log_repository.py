from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, cast, Date
from typing import Dict, Any, List, Tuple
from src.modules.auth_service.src.application.ports.auditoria_log_repository import IAuditoriaLogRepository
from src.modules.auth_service.src.infrastructure.api.schemas.auditoria import AuditoriaLogFilters
from src.modules.auth_service.src.infrastructure.db.models import AuditoriaLogORM
from src.shared.exceptions import RepositoryError

class AuditoriaLogRepository(IAuditoriaLogRepository):
    
    def __init__(self, db: Session):
        self.db = db # Esta es la sesión de la DB interna (auth)

    def create_log(self, log_data: Dict[str, Any]) -> bool:
        """
        Crea un nuevo registro de log en la base de datos.
        'log_data' es un diccionario que coincide con las columnas de AuditoriaLogORM.
        """
        try:
            db_log = AuditoriaLogORM(**log_data)
            self.db.add(db_log)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            # Loguear este error es importante, pero no deberíamos
            # fallar la petición principal del usuario si el log falla.
            print(f"Error al escribir en log de auditoría: {e}")
            return False
        
    def _apply_filters(self, query, filters: AuditoriaLogFilters):
        """Aplica los filtros de búsqueda a una query de AuditoriaLogORM."""
        if filters.ejecutado_por_id is not None:
            query = query.filter(AuditoriaLogORM.ejecutado_por_id == filters.ejecutado_por_id)
        if filters.accion:
            query = query.filter(AuditoriaLogORM.accion == filters.accion)
        if filters.modelo:
            query = query.filter(AuditoriaLogORM.modelo == filters.modelo)
        if filters.fecha:
            # Compara solo la parte de la fecha de la columna DateTime
            query = query.filter(cast(AuditoriaLogORM.fecha, Date) == filters.fecha)
            # Alternativa si cast no funciona bien con tu DB/driver:
            # query = query.filter(func.date(AuditoriaLogORM.fecha) == filters.fecha)
        return query

    def count_by_filters(self, filters: AuditoriaLogFilters) -> int:
        """Cuenta logs según los filtros proporcionados."""
        try:
            query = self.db.query(func.count(AuditoriaLogORM.log_id))
            query = self._apply_filters(query, filters)
            return query.scalar() or 0
        except SQLAlchemyError as e:
            raise RepositoryError("Error al contar los logs de auditoría.") from e
        
    def get_paginated_by_filters(
        self, filters: AuditoriaLogFilters, page: int, page_size: int
    ) -> Tuple[List[AuditoriaLogORM], int]:
        """Obtiene logs paginados según filtros y devuelve ORMs y conteo."""
        try:
            # 1. Obtener conteo total
            total_records = self.count_by_filters(filters)
            
            if total_records == 0:
                return [], 0
                
            # 2. Obtener datos paginados
            query = self.db.query(AuditoriaLogORM)
            query = self._apply_filters(query, filters)
            
            # Ordenar (ej. por fecha descendente)
            query = query.order_by(AuditoriaLogORM.fecha.desc())
            
            # Paginación
            offset = (page - 1) * page_size
            query = query.limit(page_size).offset(offset)
            
            orm_list = query.all()
            
            return orm_list, total_records
            
        except SQLAlchemyError as e:
            raise RepositoryError("Error al obtener logs de auditoría paginados.") from e