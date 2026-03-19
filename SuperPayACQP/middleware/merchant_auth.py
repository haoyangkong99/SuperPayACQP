"""
Merchant Authentication Middleware
Validates Merchant-ID header for all API requests
"""
import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class MerchantAuthMiddleware:
    """
    Validates Merchant-ID header for all API requests
    """
    
    # Paths that don't require merchant authentication
    EXEMPT_PATHS = [
        '/health',
        '/alipay/notifyPayment',
        '/api/schema/',
        '/api/docs/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip authentication for exempt paths
        if self._is_exempt_path(request.path):
            return self.get_response(request)
        
        # Get merchant ID from header
        merchant_id = request.headers.get('Merchant-ID')
        
        if not merchant_id:
            logger.warning(f"Missing Merchant-ID header for path: {request.path}")
            return JsonResponse({
                'result': {
                    'resultCode': 'MISSING_MERCHANT_ID',
                    'resultStatus': 'F',
                    'resultMessage': 'Merchant-ID header is required'
                }
            }, status=403)
        
        # Validate merchant exists
        try:
            from apps.merchants.models import Merchant
            merchant = Merchant.objects.get(merchantId=merchant_id)
            request.merchant = merchant
            logger.debug(f"Merchant authenticated: {merchant_id}")
        except Merchant.DoesNotExist:
            logger.warning(f"Invalid Merchant-ID: {merchant_id}")
            return JsonResponse({
                'result': {
                    'resultCode': 'INVALID_MERCHANT',
                    'resultStatus': 'F',
                    'resultMessage': 'Invalid Merchant-ID'
                }
            }, status=403)
        except Exception as e:
            logger.error(f"Error validating merchant: {e}")
            return JsonResponse({
                'result': {
                    'resultCode': 'INTERNAL_ERROR',
                    'resultStatus': 'F',
                    'resultMessage': 'Internal server error'
                }
            }, status=500)
        
        return self.get_response(request)
    
    def _is_exempt_path(self, path: str) -> bool:
        """Check if path is exempt from authentication"""
        for exempt_path in self.EXEMPT_PATHS:
            if path.startswith(exempt_path):
                return True
        return False
