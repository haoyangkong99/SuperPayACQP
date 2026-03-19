"""
Helper Functions for SuperPayACQP
"""
import uuid
from datetime import datetime, timezone, timedelta


def generate_uuid() -> str:
    """Generate a UUID string"""
    return str(uuid.uuid4())


def get_current_utc_time() -> datetime:
    """Get current UTC time"""
    return datetime.now(timezone.utc)


def get_expiry_time(minutes: int = 1) -> datetime:
    """
    Get expiry time from now
    
    Args:
        minutes: Number of minutes until expiry
        
    Returns:
        Expiry datetime
    """
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)


def format_iso_datetime(dt: datetime) -> str:
    """
    Format datetime to ISO 8601 string
    
    Args:
        dt: Datetime object
        
    Returns:
        ISO 8601 formatted string
    """
    return dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")


def is_expired(expiry_time: datetime) -> bool:
    """
    Check if a datetime is expired
    
    Args:
        expiry_time: Expiry datetime
        
    Returns:
        True if expired, False otherwise
    """
    return datetime.now(timezone.utc) > expiry_time
