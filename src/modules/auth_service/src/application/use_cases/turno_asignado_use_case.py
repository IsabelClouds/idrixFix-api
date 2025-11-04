from typing import List, Dict, Any
from src.modules.auth_service.src.application.ports.usuarios import IUsuarioRepository
from src.modules.auth_service.src.application.ports.turno_asignado_repository import ITurnoAsignadoRepository
from src.modules.auth_service.src.application.ports.turno_externo_repository import ITurnoExternaRepository
from src.modules.auth_service.src.application.use_cases.audit_use_case import AuditUseCase
from src.modules.auth_service.src.infrastructure.db.models import UsuarioTurnoAsignado
from src.shared.exceptions import NotFoundError, ValidationError, AlreadyExistsError

class TurnoAsignadoUseCase:
    
    def __init__(
        self,
        usuario_repository: IUsuarioRepository,
        turno_asignado_repository: ITurnoAsignadoRepository,
        turno_externa_repository: ITurnoExternaRepository,
        audit_use_case: AuditUseCase
    ):
        self.usuario_repository = usuario_repository
        self.turno_asignado_repository = turno_asignado_repository
        self.turno_externa_repository = turno_externa_repository
        self.audit_use_case = audit_use_case

    def get_turnos_por_usuario(self, id_usuario: int) -> List[UsuarioTurnoAsignado]:
        """Obtiene los turnos asignados a un usuario"""
        usuario = self.usuario_repository.get_by_id(id_usuario)
        if not usuario:
            raise NotFoundError(f"Usuario con id={id_usuario} no encontrado.")
        
        return self.turno_asignado_repository.get_by_usuario_id(id_usuario)

    def asignar_turno(
        self, id_usuario: int, id_turno_externo: int, user_data: Dict[str, Any]
    ) -> UsuarioTurnoAsignado:
        """Asigna un turno a un usuario, validando existencias y auditando."""
        
        # 1. Validar que el usuario existe
        usuario = self.usuario_repository.get_by_id(id_usuario)
        if not usuario:
            raise NotFoundError(f"Usuario con id={id_usuario} no encontrado.")

        # 2. Validar que el turno externo existe y está activo
        if not self.turno_externa_repository.exists_by_id(id_turno_externo):
            raise NotFoundError(f"Turno externo con id={id_turno_externo} no existe o está inactivo.")

        # 3. Asignar el turno
        nueva_asignacion = self.turno_asignado_repository.asignar(id_usuario, id_turno_externo)

        # 4. Registrar en auditoría
        try:
            self.audit_use_case.log_action(
                accion="CREATE",
                user_id=user_data.get("user_id"),
                modelo="UsuarioTurnoAsignado",
                entidad_id=str(nueva_asignacion.id_usuario_turno),
                datos_nuevos={
                    "id_usuario": id_usuario,
                    "id_turno_externo": id_turno_externo
                }
            )
        except Exception as e:
            print(f"Error al registrar auditoría de asignación de turno: {e}")
            
        return nueva_asignacion

    def remover_turno(
        self, id_usuario: int, id_turno_externo: int, user_data: Dict[str, Any]
    ) -> bool:
        """Remueve una asignación de turno y audita."""
        
        # 1. Validar que el usuario existe
        usuario = self.usuario_repository.get_by_id(id_usuario)
        if not usuario:
            raise NotFoundError(f"Usuario con id={id_usuario} no encontrado.")

        # 2. Remover el turno
        resultado = self.turno_asignado_repository.remover(id_usuario, id_turno_externo)

        # 3. Registrar en auditoría
        try:
            self.audit_use_case.log_action(
                accion="DELETE",
                user_id=user_data.get("user_id"),
                modelo="UsuarioTurnoAsignado",
                entidad_id=f"u{id_usuario}-t{id_turno_externo}", # ID compuesto para el log
                datos_anteriores={
                    "id_usuario": id_usuario,
                    "id_turno_externo": id_turno_externo
                }
            )
        except Exception as e:
            print(f"Error al registrar auditoría de remoción de turno: {e}")

        return resultado