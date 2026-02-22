from abc import abstractmethod, ABC
from typing import Optional, List

from src.modules.administracion_service.src.domain.entities import TipoLimpieza


class ITipoLimpiezaRepository(ABC):

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[TipoLimpieza]:
        pass

    @abstractmethod
    def get_all(self) -> List[TipoLimpieza]:
        pass