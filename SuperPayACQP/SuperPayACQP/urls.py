"""
URL configuration for SuperPayACQP project.
"""
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.payments.views import (
    PlaceOrderView, 
    CancelPaymentView, 
    InquiryPaymentView,
    NotifyPaymentView
)
from apps.refunds.views import RefundView

urlpatterns = [
    # API Schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # SuperPayACQP Endpoints
    path('api/place-order', PlaceOrderView.as_view(), name='place-order'),
    path('api/cancel-payment', CancelPaymentView.as_view(), name='cancel-payment'),
    path('api/refund', RefundView.as_view(), name='refund'),
    path('api/inquiryPayment', InquiryPaymentView.as_view(), name='inquiry-payment'),
    
    # Alipay+ Callback
    path('alipay/notifyPayment', NotifyPaymentView.as_view(), name='notify-payment'),
]
