from typing import List, Optional, Dict, Any
from src.modules.auth_service.src.application.ports.usuarios import IUsuarioRepository
from src.modules.auth_service.src.application.ports.roles import IRolRepository
from src.modules.auth_service.src.infrastructure.api.schemas.usuarios import UsuarioCreate, UsuarioUpdate, UsuarioResponse
from src.modules.auth_service.src.infrastructure.db.models import Usuario
from src.modules.auth_service.src.domain.value_objects import Password, Username
from src.shared.exceptions import AlreadyExistsError, NotFoundError, ValidationError

#Auditoria
from src.modules.auth_service.src.application.use_cases.audit_use_case import AuditUseCase


class UsuarioUseCase:
    def __init__(
        self,
        usuario_repository: IUsuarioRepository,
        rol_repository: IRolRepository,
        audit_use_case: AuditUseCase
    ):
        self.usuario_repository = usuario_repository
        self.rol_repository = rol_repository
        self.audit_use_case = audit_use_case

    def get_all_usuarios(self) -> List[Usuario]:
        """Obtiene todos los usuarios"""
        return self.usuario_repository.get_all()

    def get_usuario_by_id(self, usuario_id: int) -> Optional[Usuario]:
        """Obtiene un usuario por ID"""
        return self.usuario_repository.get_by_id(usuario_id)

    def create_usuario(self, usuario_data: UsuarioCreate, user_data: Dict[str, Any]) -> Usuario:
        """Crea un nuevo usuario"""
        # Validar que el username no exista
        existing_user = self.usuario_repository.get_by_username(usuario_data.username)
        if existing_user:
            raise AlreadyExistsError(f"El usuario '{usuario_data.username}' ya existe.")

        # Validar formato de username
        try:
            Username(usuario_data.username)
        except ValueError as e:
            raise ValidationError(str(e))

        # Validar y hashear password
        try:
            password = Password(usuario_data.password)
            usuario_data.password_hash = password.hash()
        except ValueError as e:
            raise ValidationError(str(e))

        # Validar que el rol exista
        if usuario_data.id_rol:
            rol = self.rol_repository.get_by_id(usuario_data.id_rol)
            if not rol or not rol.is_active:
                raise NotFoundError(f"Rol con id={usuario_data.id_rol} no encontrado o inactivo.")
        
        new_usuario_orm = self.usuario_repository.create(usuario_data)
        # 2. Registrar en auditoría
        self.audit_use_case.log_action(
            accion="CREATE",
            user_id=user_data.get("user_id"),
            modelo="usuarios", # Nombre del modelo/tabla
            entidad_id=new_usuario_orm.id_usuario, # ID del nuevo registro
            datos_nuevos=usuario_data.model_dump(mode="json")
        )

        return new_usuario_orm

    def update_usuario(self, usuario_id: int, usuario_data: UsuarioUpdate, user_data: Dict[str, Any]) -> Optional[Usuario]:
        """Actualiza un usuario existente"""
        # Verificar que el usuario existe
        existing_user = self.usuario_repository.get_by_id(usuario_id)
        if not existing_user:
            raise NotFoundError(f"Usuario con id={usuario_id} no encontrado.")
        datos_anteriores = UsuarioResponse.model_validate(existing_user).model_dump(mode="json")

        # Si se actualiza username, verificar que no exista
        if usuario_data.username and usuario_data.username != existing_user.username:
            username_exists = self.usuario_repository.get_by_username(usuario_data.username)
            if username_exists:
                raise AlreadyExistsError(f"El usuario '{usuario_data.username}' ya existe.")
            
            try:
                Username(usuario_data.username)
            except ValueError as e:
                raise ValidationError(str(e))


        # Si se actualiza password, validar y hashear
        if usuario_data.password:
            try:
                password = Password(usuario_data.password)
                usuario_data.password_hash = password.hash()
            except ValueError as e:
                raise ValidationError(str(e))

        # Si se actualiza rol, verificar que exista
        if usuario_data.id_rol:
            rol = self.rol_repository.get_by_id(usuario_data.id_rol)
            if not rol or not rol.is_active:
                raise NotFoundError(f"Rol con id={usuario_data.id_rol} no encontrado o inactivo.")

        updated_user_orm = self.usuario_repository.update(usuario_id, usuario_data)
        # 3. Registrar en auditoría
        self.audit_use_case.log_action(
            accion="UPDATE",
            user_id=user_data.get("user_id"),
            modelo="usuarios",
            entidad_id=usuario_id,
            datos_nuevos=usuario_data.model_dump(mode="json", exclude_unset=True), # ¡Serializar!
            datos_anteriores=datos_anteriores
        )
        return updated_user_orm

    def delete_usuario(self, usuario_id: int, user_data: Dict[str, Any],) -> Optional[Usuario]:
        """Elimina (desactiva) un usuario"""
        usuario = self.usuario_repository.get_by_id(usuario_id)
        if not usuario:
            raise NotFoundError(f"Usuario con id={usuario_id} no encontrado.")
        datos_anteriores = UsuarioResponse.model_validate(usuario).model_dump(mode="json")
        updated_user = self.usuario_repository.soft_delete(usuario_id)
        # 3. Registrar en auditoría
        self.audit_use_case.log_action(
            accion="DELETE",
            user_id=user_data.get("user_id"),
            modelo="usuarios",
            entidad_id=usuario_id,
            datos_nuevos=UsuarioResponse.model_validate(updated_user).model_dump(mode="json", exclude_unset=True), # ¡Serializar!
            datos_anteriores=datos_anteriores
        )
        return updated_user

    def activate_usuario(self, usuario_id: int, user_data: Dict[str, Any]) -> Optional[Usuario]:
        """Activa un usuario"""
        usuario = self.usuario_repository.get_by_id(usuario_id)
        if not usuario:
            raise NotFoundError(f"Usuario con id={usuario_id} no encontrado.")

        if usuario.is_active:
            raise ValidationError("El usuario ya está activo.")
        datos_anteriores = UsuarioResponse.model_validate(usuario).model_dump(mode="json")

        # Crear datos de actualización para activar
        update_data = UsuarioUpdate(is_active=True)
        updated_user = self.usuario_repository.update(usuario_id, update_data)
        # 3. Registrar en auditoría
        self.audit_use_case.log_action(
            accion="UPDATE",
            user_id=user_data.get("user_id"),
            modelo="usuarios",
            entidad_id=usuario_id,
            datos_nuevos=UsuarioResponse.model_validate(updated_user).model_dump(mode="json", exclude_unset=True), # ¡Serializar!
            datos_anteriores=datos_anteriores
        )
        return updated_user

    def change_password(self, usuario_id: int, current_password: str, new_password: str) -> bool:
        """Cambia la contraseña de un usuario"""
        usuario = self.usuario_repository.get_by_id(usuario_id)
        if not usuario:
            raise NotFoundError(f"Usuario con id={usuario_id} no encontrado.")

        # Verificar contraseña actual
        if not Password.verify(current_password, usuario.password_hash):
            raise ValidationError("Contraseña actual incorrecta.")

        # Validar nueva contraseña
        try:
            new_password_obj = Password(new_password)
            password_hash = new_password_obj.hash()
        except ValueError as e:
            raise ValidationError(str(e))

        # Actualizar contraseña
        update_data = UsuarioUpdate(password_hash=password_hash)
        result = self.usuario_repository.update(usuario_id, update_data)
        return result is not None

    def update_password(self, usuario_id: int, new_password: str) -> bool:
        """Cambia la contraseña de un usuario"""
        usuario = self.usuario_repository.get_by_id(usuario_id)
        if not usuario:
            raise NotFoundError(f"Usuario con id={usuario_id} no encontrado.")

        # Validar nueva contraseña
        try:
            new_password_obj = Password(new_password)
            password_hash = new_password_obj.hash()
        except ValueError as e:
            raise ValidationError(str(e))

        # Actualizar contraseña
        update_data = UsuarioUpdate(password_hash=password_hash)
        result = self.usuario_repository.update(usuario_id, update_data)

        self.audit_use_case.log_action(
            accion="UPDATE",
            user_id=usuario_id,
            modelo="usuarios",
            entidad_id=usuario_id,
        )

        return result is not None