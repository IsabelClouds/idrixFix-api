import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Agrega la raíz del proyecto al path para encontrar los módulos
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

# Importa configuración centralizada
from src.shared.config import settings
# Usar _BaseAuth como la base declarativa a migrar
from src.shared.database import _BaseAuth as target_base 

# Importar models.py para registrar todos los modelos en sus bases
# Esto asegura que los modelos de Auth se registren en _BaseAuth
import src.shared.models

# Configura la URL de la base de datos desde tu archivo de configuración central
config = context.config
# Usar la URL de la base de datos de AUTENTICACIÓN
config.set_main_option("sqlalchemy.url", settings.auth_database_url)

# Interpreta el archivo de configuración para el logging de Python.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# El `target_metadata` apunta a la metadata de la base de AUTH para la autogeneración
target_metadata = target_base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        # Configuraciones específicas para SQL Server
        connect_args={
            "timeout": 30,
            "autocommit": False,
        },
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()