"""
JWT Authentication Middleware
Validates JWT token for all API requests
"""
import logging
from django.http import JsonResponse
from django.contrib.auth.models import User
from utils.jwt_utils import decode_jwt_token

logger = logging.getLogger(__name__)


class JWTAuthMiddleware:
    """
    Validates JWT token for all API requests
    Replaces the previous Merchant-ID header authentication
    """
    
    # Paths that don't require JWT authentication
    # Note: Frontend pages use Django session auth, API endpoints use JWT
    EXEMPT_PATHS = [
        # Health check
        '/health',
        # Alipay+ callback (no auth required)
        '/alipay/notifyPayment',
        # API docs
        '/api/schema/',
        '/api/docs/',
        # Auth endpoints (public)
        '/api/auth/login',
        '/api/auth/register',
        '/api/auth/csrf',
        '/api/auth/token/refresh',
        '/api/auth/profile',
        '/api/inquiry-payment',
        # Query endpoints (use session auth for dashboard)
        '/api/query/',
        # Entry code endpoints
        '/entry-code',
        '/entry-code/confirm',
        # Frontend pages (use Django session auth)
        '/login',
        '/register',
        '/dashboard',
        '/create-order',
        '/view-orders',
        '/checkout',
        '/payment',
        '/payment-result',
        '/manage-goods',
        '/manage-merchants',
        '/generate-code',
        # Static files
        '/static/',
        '/favicon.ico',
        '/.well-known/',  # Chrome DevTools requests
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip authentication for exempt paths
        if self._is_exempt_path(request.path):
            logger.debug(f"JWT Auth: Path is exempt: {request.path}")
            return self.get_response(request)
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            logger.warning(f"Missing or invalid Authorization header for path: {request.path}")
            return JsonResponse({
                'result': {
                    'resultCode': 'MISSING_TOKEN',
                    'resultStatus': 'F',
                    'resultMessage': 'Authorization header with Bearer token is required'
                }
            }, status=401)
        
        token = auth_header.split(' ')[1]
        
        # Decode and validate JWT token
        payload = decode_jwt_token(token)
        
        if payload is None:
            logger.warning(f"Invalid or expired JWT token for path: {request.path}")
            return JsonResponse({
                'result': {
                    'resultCode': 'INVALID_TOKEN',
                    'resultStatus': 'F',
                    'resultMessage': 'Invalid or expired token'
                }
            }, status=401)
        
        # Extract user info from token
        user_id = payload.get('user_id')
        session_id = payload.get('session_id')
        
        if user_id is None:
            logger.warning(f"Invalid token payload - missing user_id")
            return JsonResponse({
                'result': {
                    'resultCode': 'INVALID_TOKEN',
                    'resultStatus': 'F',
                    'resultMessage': 'Invalid token payload'
                }
            }, status=401)
        
        # Get user from database
        try:
            user = User.objects.get(id=user_id)
            request.user = user
            request.jwt_payload = payload
            request.session_id = session_id
            logger.debug(f"JWT authenticated user: {user.username} (id: {user_id})")
        except User.DoesNotExist:
            logger.warning(f"User not found for id: {user_id}")
            return JsonResponse({
                'result': {
                    'resultCode': 'USER_NOT_FOUND',
                    'resultStatus': 'F',
                    'resultMessage': 'User not found'
                }
            }, status=401)
        except Exception as e:
            logger.error(f"Error validating user: {e}")
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


# Keep backward compatibility alias
MerchantAuthMiddleware = JWTAuthMiddleware
