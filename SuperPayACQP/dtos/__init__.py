"""
Base DTO Classes
"""
from pydantic import BaseModel
from typing import Optional, Any, Dict
from utils.constants import Result


class AmountDTO(BaseModel):
    """Amount DTO for payment amounts"""
    currency: Optional[str] = None
    value: int


class BaseRequestDTO(BaseModel):
    """Base class for all request DTOs"""

    class Config:
        extra = 'forbid'  # Reject extra fields


class BaseResponseDTO(BaseModel):
    """Base class for all response DTOs"""
    result: Result

    class Config:
        extra = 'allow'  # Allow extra fields in responses
