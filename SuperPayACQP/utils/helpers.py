"""
Helper Functions for SuperPayACQP
"""
import uuid
from datetime import datetime, timezone, timedelta
from dateutil import parser

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

def format_str_to_datetime(dt: str) -> datetime:
    """
    Parse datetime string to datetime object.
    Handles multiple formats including ISO 8601 with timezone.
    
    Args:
        dt: Datetime string
        
    Returns:
        Datetime object
    """
    if not dt:
        raise ValueError("Empty datetime string")
    
    # Try different formats
    formats = [
        '%Y-%m-%dT%H:%M:%S%z',      # ISO 8601 with timezone (e.g., 2026-03-23T20:01:54+08:00)
        '%Y-%m-%dT%H:%M:%S.%f%z',   # ISO 8601 with microseconds and timezone
        '%Y-%m-%dT%H:%M:%SZ',       # ISO 8601 UTC
        '%Y-%m-%dT%H:%M:%S.%fZ',    # ISO 8601 UTC with microseconds
        '%Y-%m-%dT%H:%M:%S',        # ISO 8601 without timezone
        '%Y-%m-%dT%H:%M:%S.%f',     # ISO 8601 with microseconds without timezone
        '%Y-%m-%d %H:%M:%S',        # Standard datetime format
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(dt, fmt)
        except ValueError:
            continue
    
    # If all formats fail, try using dateutil if available, otherwise raise error
    try:
        
        return parser.parse(dt)
    except ImportError:
        raise ValueError(f"Unable to parse datetime string: {dt}. Format not recognized.")

def is_expired(expiry_time: datetime) -> bool:
    """
    Check if a datetime is expired
    
    Args:
        expiry_time: Expiry datetime
        
    Returns:
        True if expired, False otherwise
    """
    return datetime.now(timezone.utc) > expiry_time
