"""
URL configuration for SuperPayACQP project.
"""
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.payments.payments_views import (
    PlaceOrderView, 
    CancelPaymentView, 
    InquiryPaymentView,
    NotifyPaymentView,
    
)
from apps.merchants.merchants_views import MerchantView, GenerateEntryCodeView, EntryCodeView, EntryCodeConfirmView
from apps.refunds.refund_views import RefundView

urlpatterns = [
    # API Schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # SuperPayACQP Endpoints
    path('api/place-order', PlaceOrderView.as_view(), name='place-order'),
    path('api/cancel-payment', CancelPaymentView.as_view(), name='cancel-payment'),
    path('api/refund', RefundView.as_view(), name='refund'),
    path('api/inquiry-payment', InquiryPaymentView.as_view(), name='inquiry-payment'),
    path('api/generate-entry-code', GenerateEntryCodeView.as_view(), name='generate-entry-code'),
    path('entry-code', EntryCodeView.as_view(), name='entry-code'),
    path('entry-code/confirm', EntryCodeConfirmView.as_view(), name='entry-code-confirm'),
    
    # Alipay+ Callback
    path('alipay/notifyPayment', NotifyPaymentView.as_view(), name='notify-payment'),

    path('api/merchants', MerchantView.as_view(), name='create-merchant'),
    
    # Query Endpoints
    path('api/query/', include('apps.query.urls')),
    
    # Auth Endpoints
    path('api/auth/', include('apps.user_auth.urls')),
    
    # Frontend Pages
    path('', include('apps.frontend.urls')),
]
