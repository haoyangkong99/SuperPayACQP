"""
Authentication Views
Login, Logout, Register API endpoints
"""
import logging
import uuid
import hashlib
import re
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from apps.users.users_models import User

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def validate_password(password: str) -> dict:
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
    Register a new user
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
        validation = validate_password(password)
        if not validation['valid']:
            return Response({
                'error': validation['errors']
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return Response({
                'error': 'Email already registered'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if username already exists
        if User.objects.filter(name=username).exists():
            return Response({
                'error': 'Username already taken'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create user
            user = User.objects.create(
                userId=str(uuid.uuid4()),
                name=username,
                email=email,
                password=hash_password(password)
            )
            
            return Response({
                'message': 'User registered successfully',
                'user': {
                    'userId': user.userId,
                    'username': user.name,
                    'email': user.email
                }
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
    Login user and return session token
    """
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        # Validate required fields
        if not email or not password:
            return Response({
                'error': 'Email and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Find user by email
            user = User.objects.filter(email=email).first()
            
            if not user:
                return Response({
                    'error': 'Invalid email or password'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Verify password
            if user.password != hash_password(password):
                return Response({
                    'error': 'Invalid email or password'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Generate session token
            session_token = str(uuid.uuid4())
            
            return Response({
                'message': 'Login successful',
                'user': {
                    'userId': user.userId,
                    'username': user.name,
                    'email': user.email
                },
                'token': session_token
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error logging in user: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    """
    POST /api/auth/logout
    Logout user
    """
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        # In a real implementation, you would invalidate the session token
        # For now, we just return a success message
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class UserProfileView(APIView):
    """
    GET /api/auth/profile
    Get user profile by userId
    """
    authentication_classes = []
    permission_classes = []
    
    def get(self, request):
        user_id = request.query_params.get('userId')
        
        if not user_id:
            return Response({
                'error': 'userId is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.filter(userId=user_id).first()
            
            if not user:
                return Response({
                    'error': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            return Response({
                'user': {
                    'userId': user.userId,
                    'username': user.name,
                    'email': user.email,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'updated_at': user.updated_at.isoformat() if user.updated_at else None,
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching user profile: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
