from typing import List
from src.modules.auth_service.src.application.ports.usuarios import IUsuarioRepository
from src.modules.auth_service.src.application.ports.lineas_asignadas import ILineaAsignadaRepository
# Asumo que crearás este puerto para la DB externa
from src.modules.auth_service.src.infrastructure.db.repositories.linea_externa_repository import ILineaExternaRepository
from src.modules.auth_service.src.infrastructure.db.models import UsuarioLineaAsignada
from src.shared.exceptions import NotFoundError, ValidationError, AlreadyExistsError

class LineaAsignadaUseCase:
    def __init__(
        self,
        usuario_repository: IUsuarioRepository,
        linea_asignada_repository: ILineaAsignadaRepository,
        linea_externa_repository: ILineaExternaRepository 
    ):
        self.usuario_repository = usuario_repository
        self.linea_asignada_repository = linea_asignada_repository
        self.linea_externa_repository = linea_externa_repository

    def get_lineas_por_usuario(self, id_usuario: int) -> List[UsuarioLineaAsignada]:
        """Obtiene las líneas asignadas a un usuario"""
        usuario = self.usuario_repository.get_by_id(id_usuario)
        if not usuario:
            raise NotFoundError(f"Usuario con id={id_usuario} no encontrado.")
        
        return self.linea_asignada_repository.get_by_usuario_id(id_usuario)

    def asignar_linea(self, id_usuario: int, id_linea_externa: int) -> UsuarioLineaAsignada:
        """Asigna una línea a un usuario, validando existencias"""
        usuario = self.usuario_repository.get_by_id(id_usuario)
        if not usuario:
            raise NotFoundError(f"Usuario con id={id_usuario} no encontrado.")

        if not self.linea_externa_repository.exists_by_id(id_linea_externa):
            raise NotFoundError(f"Línea externa con id={id_linea_externa} no existe.")

        return self.linea_asignada_repository.asignar(id_usuario, id_linea_externa)

    def remover_linea(self, id_usuario: int, id_linea_externa: int) -> bool:
        """Remueve una asignación de línea"""
        usuario = self.usuario_repository.get_by_id(id_usuario)
        if not usuario:
            raise NotFoundError(f"Usuario con id={id_usuario} no encontrado.")

        return self.linea_asignada_repository.remover(id_usuario, id_linea_externa)