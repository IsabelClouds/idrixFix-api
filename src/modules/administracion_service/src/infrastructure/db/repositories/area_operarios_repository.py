from datetime import datetime
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.modules.administracion_service.src.application.ports.area_operarios import IAreaOperarioRepository
from src.modules.administracion_service.src.domain.entities import AreaOperarios
from src.modules.administracion_service.src.infrastructure.api.schemas.area_operarios import AreaOperariosRequest
from src.modules.administracion_service.src.infrastructure.db.models import AreaOperariosORM
from src.shared.exceptions import RepositoryError, NotFoundError


class AreaOperariosRepository(IAreaOperarioRepository):

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[AreaOperarios]:
        try:
            areas_orm = (
                self.db.query(AreaOperariosORM)
                .all()
            )

            return [
                AreaOperarios(
                    area_id=a.AREA_ID,
                    area_nombre=a.AREA_NOMBRE,
                    area_estado=a.AREA_ESTADO,
                    area_feccre=a.AREA_FECCRE,
                    area_fecmod=a.AREA_FECMOD,
                )
                for a in areas_orm
            ]

        except SQLAlchemyError as e:
            raise RepositoryError("Error al obtener las areas de operarios") from e

    def get_by_id(self, id: int) -> Optional[AreaOperarios]:
        try:
            area_orm = (
                self.db.query(AreaOperariosORM)
                .filter(AreaOperariosORM.AREA_ID == id)
                .first()
            )
            if not area_orm:
                return None

            return AreaOperarios(
                area_id=area_orm.AREA_ID,
                area_nombre=area_orm.AREA_NOMBRE,
                area_estado=area_orm.AREA_ESTADO,
                area_feccre=area_orm.AREA_FECCRE,
                area_fecmod=area_orm.AREA_FECMOD
            )
        except SQLAlchemyError as e:
            raise RepositoryError("Error al consultar el area.") from e


    def exists_by_name(self, nombre: str) -> bool:
        try:
            area_orm = (
                self.db.query(AreaOperariosORM.AREA_ID)
                .filter(
                    AreaOperariosORM.AREA_NOMBRE == nombre
                )
                .first()
            )
            return area_orm is not None
        except SQLAlchemyError as e:
            raise RepositoryError("Error al consultar existencia del area operarios.") from e


    def create(self, data: AreaOperariosRequest) -> Optional[AreaOperarios]:
        try:
            area_orm = AreaOperariosORM(
                AREA_NOMBRE=data.area_nombre
            )

            self.db.add(area_orm)
            self.db.commit()
            self.db.refresh(area_orm)
            return AreaOperarios(
                area_id=area_orm.AREA_ID,
                area_nombre=area_orm.AREA_NOMBRE,
                area_estado=area_orm.AREA_ESTADO,
                area_feccre=area_orm.AREA_FECCRE,
                area_fecmod=area_orm.AREA_FECMOD
            )

        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError("Error al crear el area de operarios.") from e


    def update(self, data: AreaOperariosRequest, id: int) -> Optional[AreaOperarios]:
        try:
            area_orm = self.db.query(AreaOperariosORM).get(id)

            if area_orm is None:
                raise NotFoundError("Area de operarios no encontrada")

            area_orm.AREA_NOMBRE = data.area_nombre
            area_orm.AREA_FECMOD = datetime.now()
            self.db.commit()
            self.db.refresh(area_orm)

            return AreaOperarios(
                area_id=area_orm.AREA_ID,
                area_nombre=area_orm.AREA_NOMBRE,
                area_estado=area_orm.AREA_ESTADO,
                area_feccre=area_orm.AREA_FECCRE,
                area_fecmod=area_orm.AREA_FECMOD
            )

        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError("Error al actualizar el código de parrilla de la línea entrada.") from e
