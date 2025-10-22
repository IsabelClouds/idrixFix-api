from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError
from datetime import datetime

from src.modules.auth_service.src.infrastructure.db.models import Usuario, Rol, UsuarioLineaAsignada
from src.modules.auth_service.src.application.ports.usuarios import IUsuarioRepository
from src.modules.auth_service.src.infrastructure.api.schemas.usuarios import UsuarioCreate, UsuarioUpdate
from src.modules.auth_service.src.infrastructure.db.models import Usuario, Rol
from src.modules.auth_service.src.domain.value_objects import Password
from src.shared.exceptions import AlreadyExistsError, NotFoundError, RepositoryError


class UsuarioRepository(IUsuarioRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Usuario]:
        try:
            return (
                self.db.query(Usuario)
                .options(
                    joinedload(Usuario.rol).joinedload(Rol.permisos_modulo),
                    joinedload(Usuario.lineas_asignadas)
                )
                .filter(Usuario.is_active == True)
                .all()
            )
        except SQLAlchemyError as e:
            raise RepositoryError("Error al obtener los usuarios.") from e

    def get_by_id(self, usuario_id: int) -> Usuario:
        try:
            usuario = (
                self.db.query(Usuario)
                .options(
                    joinedload(Usuario.rol).joinedload(Rol.permisos_modulo),
                    joinedload(Usuario.lineas_asignadas)
                )
                .filter(Usuario.id_usuario == usuario_id, Usuario.is_active == True)
                .first()
            )
            if not usuario:
                raise NotFoundError(f"Usuario con id={usuario_id} no encontrado.")
            return usuario
        except SQLAlchemyError as e:
            raise RepositoryError("Error al consultar el usuario.") from e

    def get_by_username(self, username: str) -> Optional[Usuario]:
        try:
            return (
                self.db.query(Usuario)
                .options(
                    joinedload(Usuario.rol).joinedload(Rol.permisos_modulo),
                    joinedload(Usuario.lineas_asignadas)
                )
                .filter(Usuario.username == username, Usuario.is_active == True)
                .first()
            )
        except SQLAlchemyError as e:
            raise RepositoryError("Error al consultar el usuario por username.") from e

    def create(self, usuario_data: UsuarioCreate) -> Usuario:
        try:
            db_usuario = Usuario(
                username=usuario_data.username,
                password_hash=usuario_data.password_hash,
                id_rol=usuario_data.id_rol,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

            self.db.add(db_usuario)
            self.db.commit()
            self.db.refresh(db_usuario)
            return db_usuario
        except IntegrityError as e:
            self.db.rollback()
            raise AlreadyExistsError("El usuario ya existe.") from e
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError("Error al crear el usuario.") from e

    def update(self, usuario_id: int, usuario_data: UsuarioUpdate) -> Usuario:
        usuario = self.get_by_id(usuario_id)
        update_data = usuario_data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.now()

        for field, value in update_data.items():
            setattr(usuario, field, value)

        try:
            self.db.commit()
            self.db.refresh(usuario)
            return usuario
        except IntegrityError as e:
            self.db.rollback()
            if "unique constraint" in str(e.orig).lower():
                raise AlreadyExistsError(
                    f"El usuario '{usuario_data.username}' ya existe."
                )
            raise RepositoryError("Error de integridad en la base de datos.") from e
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError("Error inesperado al actualizar el usuario.") from e

    def soft_delete(self, usuario_id: int) -> Usuario:
        from sqlalchemy.sql import func

        usuario = self.get_by_id(usuario_id)
        usuario.is_active = False
        usuario.deleted_at = func.now()
        try:
            self.db.commit()
            self.db.refresh(usuario)
            return usuario
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError("No se pudo eliminar el usuario.") from e

    def authenticate(self, username: str, password: str) -> Optional[Usuario]:
        usuario = self.get_by_username(username)
        if usuario and Password.verify(password, usuario.password_hash):
            return usuario
        return None

    def update_last_login(self, usuario_id: int) -> Usuario:
        usuario = self.get_by_id(usuario_id)
        usuario.last_login = datetime.now()
        usuario.updated_at = datetime.now()
        try:
            self.db.commit()
            self.db.refresh(usuario)
            return usuario
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError("No se pudo actualizar el último login.") from e
