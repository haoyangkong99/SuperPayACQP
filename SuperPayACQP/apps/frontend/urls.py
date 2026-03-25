"""
Frontend URLs
"""
from django.urls import path
from apps.frontend.views import (
    LoginView as LoginTemplateView,
    RegisterView as RegisterTemplateView,
    DashboardView,
    GenerateCodeView,
    ManageGoodsView,
    CreateOrderView,
    CheckoutView,
    PaymentView,
    PaymentResultView,
    ViewOrdersView,
    ManageMerchantsView
)

urlpatterns = [
    # Login page
    path('login', LoginTemplateView.as_view(), name='login-page'),
    
    # Register page
    path('register', RegisterTemplateView.as_view(), name='register-page'),
    
    # Dashboard page
    path('dashboard', DashboardView.as_view(), name='dashboard-page'),
    
    # Create Order page
    path('create-order', CreateOrderView.as_view(), name='create-order-page'),
    
    # View Orders page
    path('view-orders', ViewOrdersView.as_view(), name='view-orders-page'),
    
    # Checkout page
    path('checkout', CheckoutView.as_view(), name='checkout-page'),
    
    # Payment page
    path('payment', PaymentView.as_view(), name='payment-page'),
    
    # Payment Result page
    path('payment-result', PaymentResultView.as_view(), name='payment-result-page'),
    
    # Manage Goods page
    path('manage-goods', ManageGoodsView.as_view(), name='manage-goods-page'),
    
    # Manage Merchants page
    path('manage-merchants', ManageMerchantsView.as_view(), name='manage-merchants-page'),
    
    # Generate Entry Code page
    path('generate-code', GenerateCodeView.as_view(), name='generate-code-page'),
]
