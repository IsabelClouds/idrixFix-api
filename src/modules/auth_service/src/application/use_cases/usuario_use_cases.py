from typing import List, Optional
from src.modules.auth_service.src.application.ports.usuarios import IUsuarioRepository
from src.modules.auth_service.src.application.ports.roles import IRolRepository
from src.modules.auth_service.src.infrastructure.api.schemas.usuarios import UsuarioCreate, UsuarioUpdate
from src.modules.auth_service.src.infrastructure.db.models import Usuario
from src.modules.auth_service.src.domain.value_objects import Password, Username
from src.shared.exceptions import DomainError


class UsuarioUseCase:
    def __init__(
        self,
        usuario_repository: IUsuarioRepository,
        rol_repository: IRolRepository,
    ):
        self.usuario_repository = usuario_repository
        self.rol_repository = rol_repository

    def get_all_usuarios(self) -> List[Usuario]:
        """Obtiene todos los usuarios"""
        return self.usuario_repository.get_all()

    def get_usuario_by_id(self, usuario_id: int) -> Optional[Usuario]:
        """Obtiene un usuario por ID"""
        return self.usuario_repository.get_by_id(usuario_id)

    def create_usuario(self, usuario_data: UsuarioCreate) -> Usuario:
        """Crea un nuevo usuario"""
        # Validar que el username no exista
        existing_user = self.usuario_repository.get_by_username(usuario_data.username)
        if existing_user:
            raise DomainError("El username ya existe")

        # Validar formato de username
        try:
            Username(usuario_data.username)
        except ValueError as e:
            raise DomainError(str(e))

        # Validar y hashear password
        try:
            password = Password(usuario_data.password)
            usuario_data.password_hash = password.hash()
        except ValueError as e:
            raise DomainError(str(e))

        # Validar que el rol exista
        if usuario_data.id_rol:
            rol = self.rol_repository.get_by_id(usuario_data.id_rol)
            if not rol or not rol.is_active:
                raise DomainError("Rol inválido")

        return self.usuario_repository.create(usuario_data)

    def update_usuario(self, usuario_id: int, usuario_data: UsuarioUpdate) -> Optional[Usuario]:
        """Actualiza un usuario existente"""
        # Verificar que el usuario existe
        existing_user = self.usuario_repository.get_by_id(usuario_id)
        if not existing_user:
            raise DomainError("Usuario no encontrado")

        # Si se actualiza username, verificar que no exista
        if usuario_data.username and usuario_data.username != existing_user.username:
            username_exists = self.usuario_repository.get_by_username(usuario_data.username)
            if username_exists:
                raise DomainError("El username ya existe")
            
            try:
                Username(usuario_data.username)
            except ValueError as e:
                raise DomainError(str(e))


        # Si se actualiza password, validar y hashear
        if usuario_data.password:
            try:
                password = Password(usuario_data.password)
                usuario_data.password_hash = password.hash()
            except ValueError as e:
                raise DomainError(str(e))

        # Si se actualiza rol, verificar que exista
        if usuario_data.id_rol:
            rol = self.rol_repository.get_by_id(usuario_data.id_rol)
            if not rol or not rol.is_active:
                raise DomainError("Rol inválido")

        return self.usuario_repository.update(usuario_id, usuario_data)

    def delete_usuario(self, usuario_id: int) -> Optional[Usuario]:
        """Elimina (desactiva) un usuario"""
        usuario = self.usuario_repository.get_by_id(usuario_id)
        if not usuario:
            raise DomainError("Usuario no encontrado")

        return self.usuario_repository.soft_delete(usuario_id)

    def activate_usuario(self, usuario_id: int) -> Optional[Usuario]:
        """Activa un usuario"""
        usuario = self.usuario_repository.get_by_id(usuario_id)
        if not usuario:
            raise DomainError("Usuario no encontrado")

        if usuario.is_active:
            raise DomainError("El usuario ya está activo")

        # Crear datos de actualización para activar
        update_data = UsuarioUpdate(is_active=True)
        return self.usuario_repository.update(usuario_id, update_data)

    def change_password(self, usuario_id: int, current_password: str, new_password: str) -> bool:
        """Cambia la contraseña de un usuario"""
        usuario = self.usuario_repository.get_by_id(usuario_id)
        if not usuario:
            raise DomainError("Usuario no encontrado")

        # Verificar contraseña actual
        if not Password.verify(current_password, usuario.password_hash):
            raise DomainError("Contraseña actual incorrecta")

        # Validar nueva contraseña
        try:
            new_password_obj = Password(new_password)
            password_hash = new_password_obj.hash()
        except ValueError as e:
            raise DomainError(str(e))

        # Actualizar contraseña
        update_data = UsuarioUpdate(password_hash=password_hash)
        result = self.usuario_repository.update(usuario_id, update_data)
        return result is not None
