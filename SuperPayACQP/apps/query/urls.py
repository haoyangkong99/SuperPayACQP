"""
Query API URLs
"""
from django.urls import path
from apps.query.query_views import (
    PaymentListView,
    PaymentDetailView,
    MerchantQueryView,
    RefundQueryView
)

urlpatterns = [
    # GET /api/query/payments - List all payments with orders
    path('payments', PaymentListView.as_view(), name='payment-list'),
    
    # GET /api/query/payments/detail - Get specific payment with full details
    path('payments/detail', PaymentDetailView.as_view(), name='payment-detail'),
    
    # GET /api/query/merchants - List all merchants or get specific merchant
    path('merchants', MerchantQueryView.as_view(), name='merchant-query'),
    
    # GET /api/query/refunds - Query refund records
    path('refunds', RefundQueryView.as_view(), name='refund-query'),
]
