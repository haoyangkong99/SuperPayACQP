"""
Frontend URLs
"""
from django.urls import path
from apps.frontend.views import (
    LoginView as LoginTemplateView,
    RegisterView as RegisterTemplateView,
    DashboardView,
    GenerateCodeView,
    ManageGoodsView
)

urlpatterns = [
    # Login page
    path('login/', LoginTemplateView.as_view(), name='login-page'),
    
    # Register page
    path('register/', RegisterTemplateView.as_view(), name='register-page'),
    
    # Dashboard page
    path('dashboard/', DashboardView.as_view(), name='dashboard-page'),
    
    # Manage Goods page
    path('manage-goods/', ManageGoodsView.as_view(), name='manage-goods-page'),
    
    # Generate Entry Code page
    path('generate-code/', GenerateCodeView.as_view(), name='generate-code-page'),
]
