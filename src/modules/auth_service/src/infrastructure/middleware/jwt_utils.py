"""
Utilidades para manejo y validación de tokens JWT
"""
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from src.shared.config import settings
from .exceptions import TokenInvalidException, TokenExpiredException


class JWTUtils:
    """Clase para manejo de tokens JWT"""
    
    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """
        Decodifica y valida un token JWT
        
        Args:
            token: Token JWT a decodificar
            
        Returns:
            Dict con los datos del token decodificado
            
        Raises:
            TokenInvalidException: Si el token es inválido
            TokenExpiredException: Si el token ha expirado
        """
        try:
            # Remover el prefijo 'Bearer ' si está presente
            if token.startswith('Bearer '):
                token = token[7:]
            
            # Decodificar el token
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            # Verificar expiración
            exp = payload.get('exp')
            if exp and datetime.fromtimestamp(exp) < datetime.now():
                raise TokenExpiredException()
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise TokenExpiredException()
        except jwt.InvalidTokenError:
            raise TokenInvalidException()
    
    @staticmethod
    def extract_user_id(token: str) -> int:
        """
        Extrae el ID del usuario del token JWT
        
        Args:
            token: Token JWT
            
        Returns:
            ID del usuario
        """
        payload = JWTUtils.decode_token(token)
        user_id = payload.get('sub')
        
        if not user_id:
            raise TokenInvalidException("Token no contiene ID de usuario válido")
        
        try:
            return int(user_id)
        except (ValueError, TypeError):
            raise TokenInvalidException("ID de usuario inválido en token")
    
    @staticmethod
    def extract_username(token: str) -> str:
        """
        Extrae el username del token JWT
        
        Args:
            token: Token JWT
            
        Returns:
            Username del usuario
        """
        payload = JWTUtils.decode_token(token)
        username = payload.get('username')
        
        if not username:
            raise TokenInvalidException("Token no contiene username válido")
        
        return username
    
    @staticmethod
    def extract_session_id(token: str) -> Optional[int]:
        """
        Extrae el ID de sesión del token JWT si está presente
        
        Args:
            token: Token JWT
            
        Returns:
            ID de sesión o None si no está presente
        """
        payload = JWTUtils.decode_token(token)
        session_id = payload.get('session_id')
        
        if session_id:
            try:
                return int(session_id)
            except (ValueError, TypeError):
                return None
        
        return None
    
    @staticmethod
    def is_token_valid(token: str) -> bool:
        """
        Verifica si un token es válido sin lanzar excepciones
        
        Args:
            token: Token JWT a validar
            
        Returns:
            True si el token es válido, False en caso contrario
        """
        try:
            JWTUtils.decode_token(token)
            return True
        except (TokenInvalidException, TokenExpiredException):
            return False
    
    @staticmethod
    def get_token_expiration(token: str) -> Optional[datetime]:
        """
        Obtiene la fecha de expiración del token
        
        Args:
            token: Token JWT
            
        Returns:
            Fecha de expiración o None si no está presente
        """
        try:
            payload = JWTUtils.decode_token(token)
            exp = payload.get('exp')
            if exp:
                return datetime.fromtimestamp(exp)
            return None
        except (TokenInvalidException, TokenExpiredException):
            return None
