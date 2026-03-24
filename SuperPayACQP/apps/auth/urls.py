"""
Auth API URLs
"""
from django.urls import path
from apps.auth.auth_views import (
    RegisterView,
    LoginView,
    LogoutView,
    UserProfileView
)

urlpatterns = [
    # POST /api/auth/register - Register new user
    path('register', RegisterView.as_view(), name='register'),
    
    # POST /api/auth/login - Login user
    path('login', LoginView.as_view(), name='login'),
    
    # POST /api/auth/logout - Logout user
    path('logout', LogoutView.as_view(), name='logout'),
    
    # GET /api/auth/profile - Get user profile
    path('profile', UserProfileView.as_view(), name='user-profile'),
]
