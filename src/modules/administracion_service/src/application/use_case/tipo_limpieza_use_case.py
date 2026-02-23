from typing import List

from src.modules.administracion_service.src.application.ports.tipo_limpieza import ITipoLimpiezaRepository
from src.modules.administracion_service.src.domain.entities import TipoLimpieza


class TipoLimpiezaUseCase:
    def __init__(self, tipo_limpieza_repository: ITipoLimpiezaRepository):
        self.tipo_limpieza_repository = tipo_limpieza_repository

    def get_all_tipo_limpieza(self) -> List[TipoLimpieza]:
        return self.tipo_limpieza_repository.get_all()