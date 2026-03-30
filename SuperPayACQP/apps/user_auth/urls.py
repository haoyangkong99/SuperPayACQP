"""
Auth API URLs
"""
from django.urls import path
from apps.user_auth.auth_views import (
    RegisterView,
    LoginView,
    LogoutView,
    UserProfileView,
    CSRFTokenView,
    TokenRefreshView
)

urlpatterns = [
    # GET /api/auth/csrf - Get CSRF token
    path('csrf', CSRFTokenView.as_view(), name='csrf-token'),
    
    # POST /api/auth/register - Register new user
    path('register', RegisterView.as_view(), name='register'),
    
    # POST /api/auth/login - Login user
    path('login', LoginView.as_view(), name='login'),
    
    # POST /api/auth/logout - Logout user
    path('logout', LogoutView.as_view(), name='logout'),
    
    # GET /api/auth/profile - Get user profile
    path('profile', UserProfileView.as_view(), name='user-profile'),
    
    # POST /api/auth/token/refresh - Refresh JWT token
    path('token/refresh', TokenRefreshView.as_view(), name='token-refresh'),
]
