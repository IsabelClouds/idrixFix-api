from typing import List, Optional, Dict, Any
from src.modules.auth_service.src.application.ports.usuarios import IUsuarioRepository
from src.modules.auth_service.src.application.ports.lineas_asignadas import ILineaAsignadaRepository
from src.modules.auth_service.src.infrastructure.api.schemas.usuarios import UsuarioLineaAsignadaResponse
from src.modules.auth_service.src.infrastructure.db.repositories.linea_externa_repository import ILineaExternaRepository
from src.modules.auth_service.src.infrastructure.db.models import UsuarioLineaAsignada
from src.shared.exceptions import NotFoundError, ValidationError, AlreadyExistsError
from src.modules.auth_service.src.application.use_cases.audit_use_case import AuditUseCase

class LineaAsignadaUseCase:
    def __init__(
        self,
        usuario_repository: IUsuarioRepository,
        linea_asignada_repository: ILineaAsignadaRepository,
        linea_externa_repository: ILineaExternaRepository,
        audit_use_case: AuditUseCase
    ):
        self.usuario_repository = usuario_repository
        self.linea_asignada_repository = linea_asignada_repository
        self.linea_externa_repository = linea_externa_repository
        self.audit_use_case = audit_use_case

    def get_lineas_por_usuario(self, id_usuario: int) -> List[UsuarioLineaAsignada]:
        """Obtiene las líneas asignadas a un usuario"""
        usuario = self.usuario_repository.get_by_id(id_usuario)
        if not usuario:
            raise NotFoundError(f"Usuario con id={id_usuario} no encontrado.")
        
        return self.linea_asignada_repository.get_by_usuario_id(id_usuario)

    def asignar_linea(self, id_usuario: int, id_linea_externa: int, user_data: Dict[str, Any]) -> UsuarioLineaAsignada:
        """Asigna una línea a un usuario, validando existencias"""
        usuario = self.usuario_repository.get_by_id(id_usuario)
        if not usuario:
            raise NotFoundError(f"Usuario con id={id_usuario} no encontrado.")

        if not self.linea_externa_repository.exists_by_id(id_linea_externa):
            raise NotFoundError(f"Línea externa con id={id_linea_externa} no existe.")
        nueva_asignacion = self.linea_asignada_repository.asignar(id_usuario, id_linea_externa)
        self.audit_use_case.log_action(
            accion="CREATE",
            user_id=user_data.get("user_id"),
            modelo="usuario_lineas_asignadas", # Nombre del modelo/tabla
            entidad_id=nueva_asignacion.id_usuario_linea, # ID del nuevo registro
            datos_nuevos=UsuarioLineaAsignadaResponse.model_validate(nueva_asignacion).model_dump(mode="json")
        )
        return nueva_asignacion

    def remover_linea(self, id_usuario: int, id_linea_externa: int, user_data: Dict[str, Any]) -> bool:
        """Remueve una asignación de línea"""
        usuario = self.usuario_repository.get_by_id(id_usuario)
        if not usuario:
            raise NotFoundError(f"Usuario con id={id_usuario} no encontrado.")
        linea_usuario = self.linea_asignada_repository.verificar_existencia(id_usuario, id_linea_externa)
        linea_usuario_datos = self.linea_asignada_repository.verificar_datos(id_usuario, id_linea_externa)
        if not linea_usuario:
            raise NotFoundError(f"Usuario con id={id_usuario} no encontrado en la linea {id_linea_externa}.")
        datos_anteriores = UsuarioLineaAsignadaResponse.model_validate(linea_usuario_datos).model_dump(mode="json")
        self.audit_use_case.log_action(
            accion="DELETE",
            user_id=user_data.get("user_id"),
            modelo="usuario_lineas_asignadas",
            entidad_id=linea_usuario_datos.id_usuario_linea,
            datos_anteriores=datos_anteriores
        )

        return self.linea_asignada_repository.remover(id_usuario, id_linea_externa)