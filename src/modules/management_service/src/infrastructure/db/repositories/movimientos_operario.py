# repositories.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import func, and_
from datetime import date, datetime
from typing import List, Optional, Tuple

# Importaciones de los modelos, entidades, schemas y puertos
from src.modules.management_service.src.infrastructure.db.models import WorkerMovementORM, RefDestinosMotivosORM, RefMotivosORM
from src.modules.management_service.src.domain.entities import WorkerMovement, RefMotivo, RefDestinoMotivo
from src.modules.management_service.src.infrastructure.api.schemas.movimientos_operario import (
    WorkerMovementCreate,
    WorkerMovementUpdate,
    WorkerMovementFilters
)
from src.modules.management_service.src.application.ports.movimientos_operario import (
    IWorkerMovementRepository, IRefMotivoRepository, IRefDestinoMotivoRepository
)

# Importar las excepciones de tu capa de aplicación
from src.shared.exceptions import AlreadyExistsError, NotFoundError, RepositoryError


class WorkerMovementRepository(IWorkerMovementRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_domain_entity(self, orm_model: WorkerMovementORM) -> WorkerMovement:
        """Mapea un objeto ORM a una entidad de Dominio."""
        return WorkerMovement(
            id=orm_model.id,
            linea=orm_model.linea,
            fecha_p=orm_model.fecha_p,
            tipo_movimiento=orm_model.tipo_movimiento,
            motivo=orm_model.motivo,
            codigo_operario=orm_model.codigo_operario,
            destino=orm_model.destino,
            hora=orm_model.hora,
            observacion=orm_model.observacion,
        )

    def get_by_id(self, movement_id: int) -> Optional[WorkerMovement]:
        # ESTA CONSULTA NO ESTÁ RESTRINGIDA POR LÍNEAS.
        # Si se requiere, se debe pasar 'allowed_lines' aquí también.
        try:
            movement_orm = (
                self.db.query(WorkerMovementORM)
                .filter(WorkerMovementORM.id == movement_id)
                .first()
            )
            if not movement_orm:
                return None
            return self._to_domain_entity(movement_orm)
        except SQLAlchemyError as e:
            raise RepositoryError("Error al consultar el movimiento.") from e

    def get_all_by_date(self, start_date: date, end_date: date) -> List[WorkerMovement]:
        # ESTA CONSULTA NO ESTÁ RESTRINGIDA POR LÍNEAS.
        # Si se requiere, se debe pasar 'allowed_lines' aquí también.
        try:
            orm_list = (
                self.db.query(WorkerMovementORM)
                .filter(
                    WorkerMovementORM.fecha_p >= start_date,
                    WorkerMovementORM.fecha_p <= end_date,
                )
                .order_by(WorkerMovementORM.fecha_p.desc())
                .all()
            )
            return [self._to_domain_entity(orm) for orm in orm_list]
        except SQLAlchemyError as e:
            raise RepositoryError("Error al obtener los movimientos.") from e

    def create(self, movement_data: WorkerMovementCreate) -> WorkerMovement:
        try:
            # Pydantic V2: usa model_dump()
            new_movement_orm = WorkerMovementORM(**movement_data.model_dump())
            self.db.add(new_movement_orm)
            self.db.commit()
            self.db.refresh(new_movement_orm)
            return self._to_domain_entity(new_movement_orm)
        except IntegrityError as e:
            self.db.rollback()
            raise RepositoryError("Ya existe un movimiento con esas características.") from e
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError("Error en la base de datos al crear el movimiento.") from e

    def update(
        self, movement_id: int, movement_data: WorkerMovementUpdate
    ) -> Optional[WorkerMovement]:
        movement_orm = self.db.query(WorkerMovementORM).get(movement_id)
        if not movement_orm:
            raise NotFoundError(f"Movimiento con id={movement_id} no encontrado.")
            
        update_data = movement_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(movement_orm, key, value)
            
        try:
            self.db.commit()
            self.db.refresh(movement_orm)
            return self._to_domain_entity(movement_orm)
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError("Error al actualizar el movimiento.") from e

    def delete(self, movement_id: int) -> bool:
        movement_orm = self.db.query(WorkerMovementORM).get(movement_id)
        if not movement_orm:
            raise NotFoundError(f"Movimiento con id={movement_id} no encontrado.")
        
        try:
            self.db.delete(movement_orm)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError("No se pudo eliminar el movimiento.") from e

    # +++ INICIO DE CAMBIOS +++

    def _apply_filters(
        self, query, filters: WorkerMovementFilters, allowed_lines: List[str]
    ):
        """Función auxiliar para aplicar filtros, incluyendo el filtro de seguridad de líneas."""
        conditions = []
        
        # 1. FILTRO DE SEGURIDAD OBLIGATORIO
        # El usuario solo puede consultar las líneas que tiene asignadas.
        conditions.append(WorkerMovementORM.linea.in_(allowed_lines))

        # 2. FILTROS OPCIONALES DEL USUARIO
        
        # Filtro por rango de fecha_p
        if filters.fecha_inicial and filters.fecha_final:
            conditions.append(
                WorkerMovementORM.fecha_p.between(filters.fecha_inicial, filters.fecha_final)
            )
        
        # Filtro por codigo_operario
        if filters.codigo_operario:
            conditions.append(
                WorkerMovementORM.codigo_operario == filters.codigo_operario
            )
        
        # Filtro opcional por línea (permite al usuario sub-filtrar dentro de sus líneas permitidas)
        if filters.linea:
             conditions.append(
                WorkerMovementORM.linea == filters.linea
            )
            
        # (Añadir aquí más filtros si 'filters' los tuviera, ej: tipo_movimiento)
        
        if conditions:
            query = query.filter(and_(*conditions))
            
        return query

    def count_by_filters(self, filters: WorkerMovementFilters, allowed_lines: List[str]) -> int:
        """Cuenta movimientos aplicando filtros de seguridad y de usuario."""
        try:
            # Query base para contar (más eficiente que query(WorkerMovementORM))
            query = self.db.query(func.count(WorkerMovementORM.id))
            
            # Aplicar TODOS los filtros
            query = self._apply_filters(query, filters, allowed_lines)
            
            return query.scalar() or 0 # Usar scalar() para count
        except SQLAlchemyError as e:
            raise RepositoryError("Error al contar los movimientos por filtros.") from e

    def get_paginated_by_filters(
        self, filters: WorkerMovementFilters, page: int, page_size: int, allowed_lines: List[str]
    ) -> Tuple[List[WorkerMovement], int]:
        """Obtiene movimientos paginados aplicando filtros de seguridad y de usuario."""
        try:
            # 1. Obtener el conteo total con los filtros
            # (Llama al método de conteo que ya tiene la lógica de filtros)
            total_records = self.count_by_filters(filters, allowed_lines)
            
            if total_records == 0:
                return [], 0
            
            # 2. Aplicar filtros, paginación y ordenamiento para los datos
            base_query = self.db.query(WorkerMovementORM)
            data_query = self._apply_filters(base_query, filters, allowed_lines)
            
            # Ordenar por hora/fecha para paginación consistente
            data_query = data_query.order_by(WorkerMovementORM.fecha_p.desc(), WorkerMovementORM.hora.desc())
            
            # Aplicar paginación
            offset = (page - 1) * page_size
            data_query = data_query.limit(page_size).offset(offset)
            
            orm_list = data_query.all()
            
            domain_entities = [self._to_domain_entity(orm) for orm in orm_list]
            
            return domain_entities, total_records
        except SQLAlchemyError as e:
            raise RepositoryError("Error al obtener movimientos paginados.") from e
            
    # +++ FIN DE CAMBIOS +++


# --- El resto de las clases (RefMotivoRepository, RefDestinoMotivoRepository) ---
# --- permanecen sin cambios ya que no filtran por línea. ---

class RefMotivoRepository(IRefMotivoRepository):
    def __init__(self, db: Session):
        self.db = db
        self.ACTIVE_STATUS = "ACTIVO"

    def _to_domain_entity(self, orm_model: RefMotivosORM) -> RefMotivo:
        """Mapea un objeto ORM a una entidad de Dominio (SIN created_at/updated_at)."""
        return RefMotivo(
            id_motivo=orm_model.id_motivo,
            descripcion=orm_model.descripcion,
            tipo_motivo=orm_model.tipo_motivo,
            es_justificado=orm_model.es_justificado,
            estado=orm_model.estado,
            # created_at/updated_at eliminados
        )

    def get_paginated_active(self, page: int, page_size: int) -> Tuple[List[RefMotivo], int]:
        try:
            # 1. Base query filtered by estado = 'ACTIVO'
            base_query = self.db.query(RefMotivosORM).filter(
                RefMotivosORM.estado == self.ACTIVE_STATUS
            )
            
            # 2. Conteo Total
            # (Modificado para usar func.count para eficiencia)
            total_records = base_query.session.query(func.count(RefMotivosORM.id_motivo)).filter(
                RefMotivosORM.estado == self.ACTIVE_STATUS
            ).scalar() or 0
            
            if total_records == 0:
                return [], 0
            
            # 3. Paginación y Datos (Ordenado por descripción)
            offset = (page - 1) * page_size
            orm_list = (
                base_query
                .order_by(RefMotivosORM.descripcion.asc())
                .limit(page_size)
                .offset(offset)
                .all()
            )
            
            domain_entities = [self._to_domain_entity(orm) for orm in orm_list]
            
            return domain_entities, total_records
        except SQLAlchemyError as e:
            raise RepositoryError("Error al obtener motivos activos paginados.") from e


class RefDestinoMotivoRepository(IRefDestinoMotivoRepository):
    def __init__(self, db: Session):
        self.db = db
        
    def _to_domain_entity(self, orm_model: RefDestinosMotivosORM) -> RefDestinoMotivo:
        """Mapea un objeto ORM a una entidad de Dominio (SIN created_at/updated_at)."""
        return RefDestinoMotivo(
            id_destino=orm_model.id_destino,
            id_motivo=orm_model.id_motivo,
            nombre_destino=orm_model.nombre_destino,
            descripcion=orm_model.descripcion,
            estado=orm_model.estado,
            # created_at/updated_at eliminados
        )

    def get_paginated_by_motivo(
        self, id_motivo: int, page: int, page_size: int
    ) -> Tuple[List[RefDestinoMotivo], int]:
        try:
            # 1. Base query filtered by id_motivo
            base_query = self.db.query(RefDestinosMotivosORM).filter(
                RefDestinosMotivosORM.id_motivo == id_motivo
            )
            
            # 2. Conteo Total
            # (Modificado para usar func.count para eficiencia)
            total_records = base_query.session.query(func.count(RefDestinosMotivosORM.id_destino)).filter(
                RefDestinosMotivosORM.id_motivo == id_motivo
            ).scalar() or 0
            
            if total_records == 0:
                return [], 0
            
            # 3. Paginación y Datos (Ordenado por nombre de destino)
            offset = (page - 1) * page_size
            orm_list = (
                base_query
                .order_by(RefDestinosMotivosORM.nombre_destino.asc())
                .limit(page_size)
                .offset(offset)
                .all()
            )
            
            domain_entities = [self._to_domain_entity(orm) for orm in orm_list]
            
            return domain_entities, total_records
        except SQLAlchemyError as e:
            raise RepositoryError("Error al obtener destinos por motivo paginados.") from e