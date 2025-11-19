"""
Archivo de registro de modelos para SQLAlchemy
Este archivo solo importa los modelos para que SQLAlchemy los registre
No crea dependencias circulares porque solo importa, no exporta
"""

# Importar todos los modelos para que SQLAlchemy los registre
# Esto permite que las relaciones entre microservicios funcionen

# Modelos del servicio de empleados
from src.modules.management_service.src.infrastructure.db.models import (
    WorkerMovementORM
)
from src.modules.auth_service.src.infrastructure.db.models import (
    Usuario, Rol, PermisoModulo, SesionUsuario
)

from src.modules.lineas_entrada_salida_service.infrastructure.db.models import ControlTaraOrm
# Este archivo solo importa para registrar los modelos
# Los microservicios NO deben importar desde aquí
# Solo lo usan main.py y alembic/env.py para tener el contexto completo
