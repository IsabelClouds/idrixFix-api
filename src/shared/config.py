# src/shared/config.py
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Auto-cargar variables de entorno desde el archivo .env correspondiente
# Buscar desde la raíz del proyecto (2 niveles arriba de src/shared)
_root = Path(__file__).resolve().parents[2]
_env_prod = _root / ".env.production"
_env_dev = _root / ".env.development"
_env_fallback = _root / ".env"

# Intentar cargar en orden de prioridad
if _env_prod.exists():
    load_dotenv(_env_prod, override=True)
    print(f"[OK] Cargadas variables desde: {_env_prod}")
elif _env_dev.exists():
    load_dotenv(_env_dev, override=True)
    print(f"[OK] Cargadas variables desde: {_env_dev}")
elif _env_fallback.exists():
    load_dotenv(_env_fallback, override=True)
    print(f"[OK] Cargadas variables desde: {_env_fallback}")
else:
    print("[WARN] No se encontraron archivos .env, usando valores por defecto")


class Settings(BaseSettings):
    # DB pieces
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_DRIVER: str
    DB_TRUST_CERTIFICATE: str
    DATABASE_URL: Optional[str] = None

    # --- DB de Autenticación y Logs ---
    AUTH_DB_HOST: str
    AUTH_DB_PORT: int
    AUTH_DB_NAME: str
    AUTH_DB_USER: str
    AUTH_DB_PASSWORD: str
    AUTH_DB_DRIVER: str
    AUTH_DB_TRUST_CERTIFICATE: str 
    AUTH_DATABASE_URL: Optional[str] = None

    # Servicios
    MANAGEMENT_SERVICE_HOST: str = "localhost"
    MANAGEMENT_SERVICE_PORT: int = 8001
    AUTH_SERVICE_HOST: str = "localhost"
    AUTH_SERVICE_PORT: int = 8002
    LINEAS_ENTRADA_SALIDA_SERVICE_HOST: str = "localhost"
    LINEAS_ENTRADA_SALIDA_SERVICE_PORT: int = 8003


    # Gateway
    GATEWAY_HOST: str = "localhost"
    GATEWAY_PORT: int = 8000

    # Entorno / logs
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # CORS Configuration
    CORS_ORIGINS: str = (
        "http://localhost,http://localhost:3000,http://localhost:5173"
    )
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = "*"
    CORS_ALLOW_HEADERS: str = "*"

    # JWT Configuration
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int

    @property
    def database_url(self) -> str:
        """Si existe DATABASE_URL (env), úsala; si no, constrúyela."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"mssql+pyodbc://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?driver={self.DB_DRIVER}&TrustServerCertificate={self.DB_TRUST_CERTIFICATE}"
        )
    @property
    def auth_database_url(self) -> str:
        """URL para la base de datos de autenticación."""
        if self.AUTH_DATABASE_URL:
            return self.AUTH_DATABASE_URL
        return (
            f"mssql+pyodbc://{self.AUTH_DB_USER}:{self.AUTH_DB_PASSWORD}"
            f"@{self.AUTH_DB_HOST}:{self.AUTH_DB_PORT}/{self.AUTH_DB_NAME}"
            f"?driver={self.AUTH_DB_DRIVER}&TrustServerCertificate={self.AUTH_DB_TRUST_CERTIFICATE}"
        )

    @property
    def management_service_url(self) -> str:
        return f"http://{self.MANAGEMENT_SERVICE_HOST}:{self.MANAGEMENT_SERVICE_PORT}"
    @property
    def auth_service_url(self) -> str:
        return f"http://{self.AUTH_SERVICE_HOST}:{self.AUTH_SERVICE_PORT}"
    @property
    def lineas_entrada_salida_service_url(self) -> str:
        return f"http://{self.LINEAS_ENTRADA_SALIDA_SERVICE_HOST}:{self.LINEAS_ENTRADA_SALIDA_SERVICE_PORT}"


    @property
    def cors_methods_list(self) -> list[str]:
        """Convierte la cadena de métodos CORS separada por comas en una lista"""
        if self.CORS_ALLOW_METHODS == "*":
            return ["*"]
        return [
            method.strip()
            for method in self.CORS_ALLOW_METHODS.split(",")
            if method.strip()
        ]

    @property
    def cors_headers_list(self) -> list[str]:
        """Convierte la cadena de headers CORS separada por comas en una lista"""
        if self.CORS_ALLOW_HEADERS == "*":
            return ["*"]
        return [
            header.strip()
            for header in self.CORS_ALLOW_HEADERS.split(",")
            if header.strip()
        ]

    @property
    def cors_origins_list(self) -> list[str]:
        """Convierte la cadena de orígenes CORS separada por comas en una lista"""
        if not self.CORS_ORIGINS.strip():
            return []
        return [
            origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()
        ]

    # Carga .env (orden preferente) y evita fallar por claves desconocidas
    model_config = SettingsConfigDict(
        env_file=[".env.production", ".env.development", ".env"],
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Instancia global
settings = Settings()
