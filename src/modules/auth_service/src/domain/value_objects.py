from dataclasses import dataclass
from typing import List
import re
import hashlib
import secrets
from datetime import datetime, timedelta

@dataclass(frozen=True)
class Username:
    """Value object para username"""
    value: str

    def __post_init__(self):
        if not self._is_valid_username(self.value):
            raise ValueError(f"Username inválido: {self.value}")

    @staticmethod
    def _is_valid_username(username: str) -> bool:
        """Valida formato de username"""
        if not username or len(username) < 3 or len(username) > 50:
            return False
        # Solo letras, números y guiones bajos
        pattern = r'^[a-zA-Z0-9_]+$'
        return bool(re.match(pattern, username))


@dataclass(frozen=True)
class Password:
    """Value object para password"""
    value: str

    def __post_init__(self):
        if not self._is_valid_password(self.value):
            raise ValueError("Password no cumple con los requisitos de seguridad")

    @staticmethod
    def _is_valid_password(password: str) -> bool:
        """Valida que el password cumpla con requisitos mínimos"""
        if not password or len(password) < 8:
            return False
        
        # Al menos una mayúscula, una minúscula, un número
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        return has_upper and has_lower and has_digit

    def hash(self) -> str:
        """Genera hash del password"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', 
                                          self.value.encode('utf-8'), 
                                          salt.encode('utf-8'), 
                                          100000)
        return f"{salt}:{password_hash.hex()}"

    @staticmethod
    def verify(password: str, hashed: str) -> bool:
        """Verifica un password contra su hash"""
        try:
            salt, stored_hash = hashed.split(':')
            password_hash = hashlib.pbkdf2_hmac('sha256',
                                              password.encode('utf-8'),
                                              salt.encode('utf-8'),
                                              100000)
            return password_hash.hex() == stored_hash
        except ValueError:
            return False


@dataclass(frozen=True)
class Token:
    """Value object para tokens JWT"""
    value: str
    expires_at: datetime

    def __post_init__(self):
        if not self.value or len(self.value) < 10:
            raise ValueError("Token inválido")

    def is_expired(self) -> bool:
        """Verifica si el token ha expirado"""
        return datetime.now() > self.expires_at

    def is_valid(self) -> bool:
        """Verifica si el token es válido"""
        return bool(self.value) and not self.is_expired()

    @classmethod
    def generate(cls, payload: dict) -> "Token":
        """Genera un nuevo token JWT"""
        import jwt
        from src.shared.config import settings
        
        # Calcular fecha de expiración
        expires_at = datetime.now() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
        
        # Agregar campos estándar de JWT
        jwt_payload = {
            **payload,
            "exp": int(expires_at.timestamp()),
            "iat": int(datetime.now().timestamp()),
            "iss": "incentivos-api"
        }
        
        # Generar JWT real
        token_data = jwt.encode(
            jwt_payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        return cls(value=token_data, expires_at=expires_at)


@dataclass(frozen=True)
class PermisosList:
    """Value object para lista de permisos"""
    permisos: List[str]

    def __post_init__(self):
        if not isinstance(self.permisos, list):
            raise ValueError("Permisos debe ser una lista")
        
        valid_permisos = {"read", "write"}
        for permiso in self.permisos:
            if permiso not in valid_permisos:
                raise ValueError(f"Permiso inválido: {permiso}")

    def has_read(self) -> bool:
        """Verifica si tiene permiso de lectura"""
        return "read" in self.permisos

    def has_write(self) -> bool:
        """Verifica si tiene permiso de escritura"""
        return "write" in self.permisos

    def has_all_permissions(self) -> bool:
        """Verifica si tiene todos los permisos"""
        return self.has_read() and self.has_write()


@dataclass(frozen=True)
class ModuloInfo:
    """Value object para información de módulo"""
    nombre: str
    permisos: PermisosList

    def __post_init__(self):
        if not self.nombre:
            raise ValueError("Nombre es requerido")

    def to_dict(self) -> dict:
        """Convierte a diccionario para respuesta JSON"""
        return {
            "nombre": self.nombre,
            "permisos": self.permisos.permisos
        }


@dataclass(frozen=True)
class UserSession:
    """Value object para información de sesión de usuario"""
    user_id: int
    username: str
    rol_nombre: str
    modulos: List[ModuloInfo]
    token: Token
    lineas_asignadas: List[int]

    def __post_init__(self):
        if self.user_id <= 0:
            raise ValueError("ID de usuario inválido")
        
        if not self.username or not self.rol_nombre:
            raise ValueError("Username y rol son requeridos")
        if not isinstance(self.lineas_asignadas, list):
            raise ValueError("Líneas asignadas debe ser una lista")

    def to_response_dict(self) -> dict:
        """Convierte a diccionario para respuesta de login"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "token": self.token.value,
            "expires_at": self.token.expires_at.isoformat(),
            "rol": {
                "nombre": self.rol_nombre,
                "modulos": [modulo.to_dict() for modulo in self.modulos]
            },
            "lineas_permitidas": self.lineas_asignadas
        }

    def is_session_valid(self) -> bool:
        """Verifica si la sesión es válida"""
        return self.token.is_valid()
