"""
Base DTO Classes
"""
from pydantic import BaseModel
from typing import Optional, Any, Dict
from enum import Enum


class ResultStatus(str, Enum):
    """Result status enumeration"""
    SUCCESS = 'S'
    FAILURE = 'F'
    UNKNOWN = 'U'


class ResultDTO(BaseModel):
    """Result DTO for API responses"""
    resultCode: str
    resultStatus: str
    resultMessage: Optional[str] = None


class AmountDTO(BaseModel):
    """Amount DTO for payment amounts"""
    currency: str
    value: int


class BaseRequestDTO(BaseModel):
    """Base class for all request DTOs"""
    
    class Config:
        extra = 'forbid'  # Reject extra fields


class BaseResponseDTO(BaseModel):
    """Base class for all response DTOs"""
    result: ResultDTO
    
    class Config:
        extra = 'allow'  # Allow extra fields in responses
