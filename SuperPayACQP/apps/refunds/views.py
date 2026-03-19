"""
Refund API Views
"""
import logging

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import RefundRecord
from apps.api_records.models import ApiRecord

from dtos.request import RefundRequestDTO
from dtos.response import RefundResponseDTO
from services.alipay_client import AlipayClient
from services.signature_service import SignatureService

logger = logging.getLogger(__name__)


def get_service_instances():
    """Get signature service and Alipay client instances"""
    signature_service = SignatureService(
        private_key=settings.ALIPAY_PRIVATE_KEY,
        public_key=settings.ALIPAY_PUBLIC_KEY,
        client_id=settings.ALIPAY_CLIENT_ID
    )
    alipay_client = AlipayClient(signature_service, settings.ALIPAY_CLIENT_ID)
    return signature_service, alipay_client


class RefundView(APIView):
    """
    POST /api/refund
    Initiate a refund request
    """
    
    def post(self, request):
        # Parse and validate request using DTO
        try:
            request_dto = RefundRequestDTO(**request.data)
        except Exception as e:
            logger.warning(f"Invalid request: {e}")
            return Response({
                'result': {
                    'resultCode': 'INVALID_REQUEST',
                    'resultStatus': 'F',
                    'resultMessage': str(e)
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get service instances
        _, alipay_client = get_service_instances()
        
        # Call Alipay+ Refund API
        response_dto = alipay_client.refund(request_dto)
        
        # Log API record
        ApiRecord.objects.create(
            api_url='/aps/api/v1/payments/refund',
            request_body=request_dto.model_dump_json(),
            response_body=response_dto.model_dump_json(),
            message_type='OUTBOUND'
        )
        
        # Save refund record if successful
        result = response_dto.result
        if result.resultStatus == 'S':
            try:
                RefundRecord.objects.create(
                    refundRequestId=request_dto.refundRequestId,
                    paymentRequestId=request_dto.paymentRequestId,
                    paymentId=request_dto.paymentId,
                    refundAmountValue=request_dto.refundAmount.value,
                    refundAmountCurrency=request_dto.refundAmount.currency,
                    refundReason=request_dto.refundReason or ''
                )
            except Exception as e:
                logger.error(f"Failed to save refund record: {e}")
        
        return Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK)
