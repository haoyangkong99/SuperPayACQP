"""
Custom Exception Handlers
"""
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for SuperPayACQP API
    
    Args:
        exc: Exception instance
        context: Context dictionary
        
    Returns:
        Response object
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Format error response according to Alipay+ style
        error_data = {
            'result': {
                'resultCode': get_error_code(response.status_code),
                'resultStatus': 'F',
                'resultMessage': get_error_message(response.data)
            }
        }
        response.data = error_data
    
    return response


def get_error_code(status_code: int) -> str:
    """
    Get error code based on HTTP status code
    
    Args:
        status_code: HTTP status code
        
    Returns:
        Error code string
    """
    error_codes = {
        400: 'INVALID_REQUEST',
        403: 'ACCESS_DENIED',
        404: 'NOT_FOUND',
        405: 'METHOD_NOT_ALLOWED',
        500: 'INTERNAL_ERROR',
    }
    return error_codes.get(status_code, 'UNKNOWN_ERROR')


def get_error_message(data) -> str:
    """
    Get error message from response data
    
    Args:
        data: Response data
        
    Returns:
        Error message string
    """
    if isinstance(data, dict):
        if 'detail' in data:
            return str(data['detail'])
        if 'message' in data:
            return str(data['message'])
        return str(data)
    elif isinstance(data, list):
        return str(data[0]) if data else 'Unknown error'
    return 'An error occurred'


class SuperPayACQPException(Exception):
    """Base exception for SuperPayACQP"""
    
    def __init__(self, code: str, message: str, status: str = 'F'):
        self.code = code
        self.message = message
        self.status = status
        super().__init__(message)


class InvalidRequestException(SuperPayACQPException):
    """Invalid request exception"""
    
    def __init__(self, message: str):
        super().__init__('INVALID_REQUEST', message)


class MerchantNotFoundException(SuperPayACQPException):
    """Merchant not found exception"""
    
    def __init__(self, merchant_id: str):
        super().__init__('MERCHANT_NOT_FOUND', f'Merchant not found: {merchant_id}')


class PaymentNotFoundException(SuperPayACQPException):
    """Payment not found exception"""
    
    def __init__(self, payment_id: str):
        super().__init__('PAYMENT_NOT_FOUND', f'Payment not found: {payment_id}')
