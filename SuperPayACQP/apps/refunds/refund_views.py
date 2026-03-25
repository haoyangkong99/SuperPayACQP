"""
Refund API Views
"""
import logging
import uuid
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .refund_models import RefundRecord
from apps.api_records.api_records_models import ApiRecord
from utils.constants import Result,MessageType,HTTPMethod
from dtos.request import RefundRequestDTO
from dtos.response import RefundResponseDTO,BaseResponseDTO
from services.alipay_client import AlipayClient
from services.signature_service import SignatureService
from typing import Optional
from services.db_service import DbService
logger = logging.getLogger(__name__)

_service_instances: Optional[tuple] = None
def get_service_instances() -> tuple[SignatureService, AlipayClient, DbService]:
    global _service_instances
    if _service_instances is None:
        signature_service = SignatureService(
                    private_key=settings.ALIPAY_PRIVATE_KEY,
        public_key=settings.ALIPAY_PUBLIC_KEY,
        client_id=settings.ALIPAY_CLIENT_ID
        )
        alipay_client = AlipayClient(signature_service, settings.ALIPAY_CLIENT_ID)
        db_service = DbService()
        _service_instances = (signature_service, alipay_client, db_service)
    return _service_instances
class RefundView(APIView):
    """
    POST /api/refund
    Initiate a refund request
    """
    def post(self, request):
        # Parse and validate request using DTO
        try:
            request_dto = RefundRequestDTO(**request.data)
            refund_request_id=str(uuid.uuid4())
            request_dto.refundRequestId=refund_request_id
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
        signature_service, alipay_client, db_service = get_service_instances()
        try:
                # Call Alipay+ Refund API
                response_dto = alipay_client.refund(request_dto)
                
                # Log API record
                db_service.createApiRecordsWithReqRes('/aps/api/v1/payments/refund',HTTPMethod.POST,request_dto,response_dto,MessageType.OUTBOUND)
                db_service.createApiRecordsWithReqRes('/api/refund',HTTPMethod.POST,request_dto,response_dto,MessageType.INBOUND)
                record=db_service.createRefundRecord(request_dto, response_dto)
                return Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK)
        except Exception as e:
                logger.error(f"Failed to save refund record: {e}")
                result = Result.returnProcessFail()
                response_dto = BaseResponseDTO(result=result
                )
                db_service.createApiRecordsWithReqRes('/api/refund',HTTPMethod.POST,request_dto,response_dto,MessageType.INBOUND)
                return Response (response_dto.model_dump(),status=status.HTTP_200_OK)
