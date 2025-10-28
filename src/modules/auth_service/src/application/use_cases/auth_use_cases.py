from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from src.modules.auth_service.src.application.ports.usuarios import IUsuarioRepository
from src.modules.auth_service.src.application.ports.roles import IRolRepository
from src.modules.auth_service.src.application.ports.permisos_modulo import IPermisoModuloRepository
from src.modules.auth_service.src.application.ports.sesiones import ISesionRepository
from src.modules.auth_service.src.infrastructure.api.schemas.auth import LoginRequest
from src.modules.auth_service.src.infrastructure.api.schemas.sesiones import SesionCreate
from src.modules.auth_service.src.domain.value_objects import Password, Token, UserSession, ModuloInfo, PermisosList
from src.shared.exceptions import NotFoundError, ValidationError, RepositoryError


class AuthUseCase:
    def __init__(
        self,
        usuario_repository: IUsuarioRepository,
        rol_repository: IRolRepository,
        permiso_repository: IPermisoModuloRepository,
        sesion_repository: ISesionRepository,
    ):
        self.usuario_repository = usuario_repository
        self.rol_repository = rol_repository
        self.permiso_repository = permiso_repository
        self.sesion_repository = sesion_repository

    def login(self, login_data: LoginRequest, ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
        try:
            """Autentica un usuario y crea una sesión"""
            # Buscar usuario por username
            usuario = self.usuario_repository.get_by_username(login_data.username)
            if not usuario:
                raise ValidationError("Credenciales inválidas.")

            # Verificar que el usuario esté activo
            if not usuario.is_active:
                raise ValidationError("Usuario inactivo.")

            # Verificar password
            if not Password.verify(login_data.password, usuario.password_hash):
                raise ValidationError("Credenciales inválidas.")

            # Obtener rol con permisos
            rol = self.rol_repository.get_with_permisos(usuario.id_rol)
            if not rol or not rol.is_active:
                raise NotFoundError("Rol inválido o inactivo.")

            # Extraer los IDs de las líneas asignadas desde el objeto usuario
            lineas_permitidas = [
                asignacion.id_linea_externa 
                for asignacion in usuario.lineas_asignadas or []
            ]

            token = Token.generate(
                payload={
                    "sub": str(usuario.id_usuario),  # Subject (user ID) - estándar JWT
                    "username": usuario.username,
                    "user_id": usuario.id_usuario, 
                }
            )
            
            # Crear sesión con el token JWT
            sesion_data = SesionCreate(
                id_usuario=usuario.id_usuario,
                token=token.value, 
                fecha_inicio=datetime.now(),
                fecha_expiracion=token.expires_at,
                ip_address=ip_address,
                user_agent=user_agent
            )
            sesion = self.sesion_repository.create(sesion_data)
            
            # Regenerar token con session_id Y las líneas
            token_with_session = Token.generate(
                payload={
                    "sub": str(usuario.id_usuario),  # Subject (user ID) - estándar JWT
                    "username": usuario.username,
                    "user_id": usuario.id_usuario,  # Mantener para compatibilidad
                    "session_id": sesion.id_sesion,
                    "lineas": lineas_permitidas
                }
            )
            
            # Actualizar sesión con el token final
            self.sesion_repository.update(sesion.id_sesion, {"token": token_with_session.value})
            token = token_with_session # Usar el token final para la respuesta

            # Actualizar último login
            self.usuario_repository.update_last_login(usuario.id_usuario)

            # Construir respuesta con permisos
            modulos = []  # Inicializar lista de módulos
            for permiso_modulo in rol.permisos_modulo or []:
                if permiso_modulo.is_active:
                    # Asegurar que 'modulo' es string
                    nombre_modulo = permiso_modulo.modulo.value if hasattr(permiso_modulo.modulo, "value") else permiso_modulo.modulo

                    # Asegurar que 'permisos' son strings
                    permisos_lista = [p.value if hasattr(p, "value") else p for p in permiso_modulo.permisos]

                    modulos.append(ModuloInfo(
                        nombre=nombre_modulo,
                        permisos=PermisosList(permisos_lista)
                    ))

            user_session = UserSession(
                user_id=usuario.id_usuario,
                is_superuser=usuario.is_superuser,
                username=usuario.username,
                rol_nombre=rol.nombre,
                modulos=modulos,
                token=token,
                lineas_asignadas=lineas_permitidas
            )

            return user_session.to_response_dict()
        except Exception as e:
            print("Error al autenticar usuario:", e)
            raise RepositoryError("Error al autenticar usuario.") from e

    def logout(self, token: str) -> bool:
        """Cierra sesión invalidando el token"""
        sesion = self.sesion_repository.invalidate_by_token(token)
        return sesion is not None

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verifica si un token es válido y retorna información del usuario"""
        sesion = self.sesion_repository.get_by_token(token)
        if not sesion or not sesion.is_active:
            return None

        # Verificar que la sesión no haya expirado
        if sesion.fecha_expiracion and datetime.now() > sesion.fecha_expiracion:
            self.sesion_repository.soft_delete(sesion.id_sesion)
            return None

        usuario = self.usuario_repository.get_by_id(sesion.id_usuario)
        if not usuario or not usuario.is_active:
            return None

        rol = self.rol_repository.get_with_permisos(usuario.id_rol)
        if not rol or not rol.is_active:
            return None
            
        lineas_permitidas = [
            asignacion.id_linea_externa 
            for asignacion in usuario.lineas_asignadas or []
        ]

        # Construir información del usuario
        modulos = []
        for permiso_modulo in rol.permisos_modulo or []:
            if permiso_modulo.is_active:
                nombre_modulo = (
                    permiso_modulo.modulo.value 
                    if hasattr(permiso_modulo.modulo, "value") 
                    else permiso_modulo.modulo
                )

                permisos_lista = [
                    p.value if hasattr(p, "value") else p 
                    for p in permiso_modulo.permisos
                ]

                modulos.append({
                    "nombre": nombre_modulo,
                    "permisos": permisos_lista
                })


        return {
            "user_id": usuario.id_usuario,
            "username": usuario.username,
            "is_superuser": usuario.is_superuser,
            "rol": {
                "id": rol.id_rol,
                "nombre": rol.nombre,
                "modulos": modulos
            },
            "lineas": lineas_permitidas 
        }

    def refresh_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Renueva un token válido"""
        user_info = self.verify_token(token)
        if not user_info:
            return None

        # Invalidar token actual
        self.sesion_repository.invalidate_by_token(token)

        # Crear nueva sesión
        new_token = Token.generate(
            payload={
                "sub": str(user_info["user_id"]),  
                "username": user_info["username"],
                "user_id": user_info["user_id"],  
                "lineas": user_info.get("lineas", [])
            }
        )

        sesion_data = SesionCreate(
            id_usuario=user_info["user_id"],
            token=new_token.value,
            fecha_inicio=datetime.now(),
            fecha_expiracion=new_token.expires_at
        )
        
        # Guardar la nueva sesión
        new_sesion = self.sesion_repository.create(sesion_data)
        
        token_with_session = Token.generate(
             payload={
                "sub": str(user_info["user_id"]),
                "username": user_info["username"],
                "user_id": user_info["user_id"],
                "lineas": user_info.get("lineas", []),
                "session_id": new_sesion.id_sesion 
            }
        )

        self.sesion_repository.update(new_sesion.id_sesion, {"token": token_with_session.value})
        new_token = token_with_session 

        return {
            "token": new_token.value,
            "expires_at": new_token.expires_at.isoformat(),
            "user": user_info
        }

    def logout_all_sessions(self, user_id: int) -> bool:
        """Cierra todas las sesiones de un usuario"""
        return self.sesion_repository.invalidate_all_by_usuario_id(user_id)

    def cleanup_expired_sessions(self) -> int:
        """Limpia sesiones expiradas"""
        return self.sesion_repository.cleanup_expired_sessions()