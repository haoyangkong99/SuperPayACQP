"""
JWT Utility Module
Handles JWT token generation, validation, and refresh
"""
import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from django.conf import settings

logger = logging.getLogger(__name__)

# JWT Configuration - use the hashed key from settings
JWT_SECRET_KEY = getattr(settings, 'JWT_SECRET_KEY', settings.SECRET_KEY)
JWT_ALGORITHM = 'HS256'


def get_session_expiry_age() -> int:
    """Get the session expiry age from Django settings (in seconds)"""
    # Default Django session expiry is 1209600 seconds (2 weeks)
    return getattr(settings, 'SESSION_COOKIE_AGE', 1209600)


def generate_jwt_token(user_id: int, session_id: str) -> str:
    """
    Generate JWT token with userid + sessionid
    
    Args:
        user_id: The user's ID
        session_id: The Django session key
        
    Returns:
        Encoded JWT token string
    """
    expiry_seconds = get_session_expiry_age()
    
    payload = {
        'user_id': user_id,
        'session_id': session_id,
        'exp': datetime.utcnow() + timedelta(seconds=expiry_seconds),
        'iat': datetime.utcnow(),
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate JWT token
    
    Args:
        token: The JWT token string
        
    Returns:
        Decoded payload dict if valid, None if invalid or expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        return None


def refresh_jwt_token(token: str) -> Optional[str]:
    """
    Refresh a valid JWT token with new expiration time
    
    Args:
        token: The current valid JWT token
        
    Returns:
        New JWT token string if valid, None if invalid
    """
    payload = decode_jwt_token(token)
    
    if payload is None:
        return None
    
    # Generate new token with same user_id and session_id
    user_id = payload.get('user_id')
    session_id = payload.get('session_id')
    
    if user_id is None or session_id is None:
        return None
    
    return generate_jwt_token(user_id, session_id)


def extract_user_id(token: str) -> Optional[int]:
    """
    Extract user_id from JWT token without full validation
    
    Args:
        token: The JWT token string
        
    Returns:
        user_id if present, None otherwise
    """
    payload = decode_jwt_token(token)
    if payload:
        return payload.get('user_id')
    return None


def extract_session_id(token: str) -> Optional[str]:
    """
    Extract session_id from JWT token without full validation
    
    Args:
        token: The JWT token string
        
    Returns:
        session_id if present, None otherwise
    """
    payload = decode_jwt_token(token)
    if payload:
        return payload.get('session_id')
    return None
