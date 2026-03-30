"""
Authentication Views
Login, Logout, Register API endpoints using Django's built-in auth system
"""
import logging
import re
import uuid
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
from utils.jwt_utils import generate_jwt_token, refresh_jwt_token, decode_jwt_token

logger = logging.getLogger(__name__)


def validate_password_strength(password: str) -> dict:
    """
    Validate password strength
    - At least 8 characters
    - At least one number
    - At least one special character (!@#$%^&*)
    """
    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one number")
    if not re.search(r'[!@#$%^&*]', password):
        errors.append("Password must contain at least one special character (!@#$%^&*)")
    
    return {"valid": len(errors) == 0, "errors": errors}


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    """
    POST /api/auth/register
    Register a new user using Django's built-in User model
    """
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        confirm_password = request.data.get('confirmPassword')
        
        # Validate required fields
        if not username or not email or not password or not confirm_password:
            return Response({
                'error': 'All fields are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if passwords match
        if password != confirm_password:
            return Response({
                'error': 'Passwords do not match'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate password strength
        validation = validate_password_strength(password)
        if not validation['valid']:
            return Response({
                'error': validation['errors']
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return Response({
                'error': 'Username already taken'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return Response({
                'error': 'Email already registered'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create user using Django's built-in User model
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password  # Django will hash the password automatically
            )
            
            # Generate a temporary session ID for the token (not stored in DB)
            # This is used only for the JWT token generation
            temp_session_id = str(uuid.uuid4())
            
            # Generate JWT token
            jwt_token = generate_jwt_token(user.id, temp_session_id)
            
            return Response({
                'message': 'User registered successfully',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                },
                'token': jwt_token
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    """
    POST /api/auth/login
    Login user using Django's built-in authentication
    """
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        
        # Support login with either username or email
        if not password:
            return Response({
                'error': 'Password is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not username and not email:
            return Response({
                'error': 'Username or email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # If email is provided, find the username
            if email and not username:
                user = User.objects.filter(email=email).first()
                if user:
                    username = user.username
                else:
                    return Response({
                        'error': 'Invalid email or password'
                    }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Authenticate using Django's built-in auth
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Login using Django's built-in login (creates session)
                login(request, user)
                
                # Get the session key (sessionid)
                session_id = request.session.session_key
                
                # Generate JWT token with user_id and session_id
                jwt_token = generate_jwt_token(user.id, session_id)
                
                return Response({
                    'message': 'Login successful',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email
                    },
                    'token': jwt_token,
                    'session_id': session_id
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Invalid username/email or password'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
        except Exception as e:
            logger.error(f"Error logging in user: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    """
    POST /api/auth/logout
    Logout user using Django's built-in logout
    """
    
    def post(self, request):
        try:
            # Logout using Django's built-in logout
            logout(request)
            
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error logging out user: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class UserProfileView(APIView):
    """
    GET /api/auth/profile
    Get user profile
    """
    
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({
                'error': 'User not authenticated'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        user = request.user
        
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined.isoformat() if user.date_joined else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
            }
        }, status=status.HTTP_200_OK)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class CSRFTokenView(APIView):
    """
    GET /api/auth/csrf
    Get CSRF token for frontend
    """
    authentication_classes = []
    permission_classes = []
    
    def get(self, request):
        return Response({
            'message': 'CSRF cookie set'
        }, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class TokenRefreshView(APIView):
    """
    POST /api/auth/token/refresh
    Refresh JWT token to extend validity
    """
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        # Get token from Authorization header or request body
        auth_header = request.headers.get('Authorization', '')
        
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            token = request.data.get('token')
        
        if not token:
            return Response({
                'error': 'Token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Refresh the token
        new_token = refresh_jwt_token(token)
        
        if new_token is None:
            return Response({
                'error': 'Invalid or expired token'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({
            'message': 'Token refreshed successfully',
            'token': new_token
        }, status=status.HTTP_200_OK)
