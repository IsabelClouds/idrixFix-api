from abc import abstractmethod, ABC
from typing import Optional

from src.modules.administracion_service.src.domain.entities import TipoLimpieza


class ITipoLimpiezaRepository(ABC):

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[TipoLimpieza]:
        pass