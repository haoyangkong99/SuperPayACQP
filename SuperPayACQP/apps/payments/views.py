"""
Payment API Views
"""
import json
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import PaymentRequest, PaymentRequestResult, Settlement
from apps.api_records.models import ApiRecord
from apps.merchants.models import Merchant

from dtos.request import (
    PlaceOrderRequestDTO, 
    CancelPaymentRequestDTO, 
    InquiryPaymentRequestDTO
)
from dtos.alipay_request import (
    AlipayPayRequestDTO, 
    PaymentMethodDTO, 
    AlipayOrderDTO,
    MerchantInfoDTO
)
from dtos.response import (
    PaymentResponseDTO, 
    CancelPaymentResponseDTO, 
    InquiryPaymentResponseDTO,
    NotifyPaymentResponseDTO
)
from dtos import ResultDTO

from services.alipay_client import AlipayClient, RetryHandler
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


class PlaceOrderView(APIView):
    """
    POST /api/place-order
    Place an order and initiate payment
    """
    
    def post(self, request):
        # Parse and validate request using DTO
        try:
            request_dto = PlaceOrderRequestDTO(**request.data)
        except Exception as e:
            logger.warning(f"Invalid request: {e}")
            return Response({
                'result': {
                    'resultCode': 'INVALID_REQUEST',
                    'resultStatus': 'F',
                    'resultMessage': str(e)
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate payment request ID
        payment_request_id = str(uuid.uuid4())
        
        # Calculate expiry time (current time + 1 minute)
        expiry_time = datetime.now(timezone.utc) + timedelta(minutes=1)
        
        # Build Alipay+ request DTO
        alipay_request_dto = self._build_alipay_request_dto(
            request_dto, 
            payment_request_id, 
            expiry_time
        )
        
        # Get service instances
        _, alipay_client = get_service_instances()
        
        # Call Alipay+ Pay API
        response_dto = alipay_client.pay(alipay_request_dto)
        
        # Log API record
        ApiRecord.objects.create(
            api_url='/aps/api/v1/payments/pay',
            request_body=json.dumps(alipay_request_dto.to_alipay_dict()),
            response_body=response_dto.model_dump_json(),
            message_type='OUTBOUND'
        )
        
        # Process result
        result = response_dto.result
        result_status = result.resultStatus
        result_code = result.resultCode
        
        # Handle PAYMENT_IN_PROCESS with retry
        if result_status == 'U' and result_code == 'PAYMENT_IN_PROCESS':
            response_dto = self._handle_payment_in_process(payment_request_id, alipay_client)
        
        # Handle UNKNOWN_EXCEPTION with retry
        elif result_status == 'U' and result_code == 'UNKNOWN_EXCEPTION':
            response_dto = alipay_client.pay(alipay_request_dto)
        
        # Save payment request to database
        self._save_payment_request(alipay_request_dto, response_dto, payment_request_id)
        
        return Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK)
    
    def _build_alipay_request_dto(self, request_dto: PlaceOrderRequestDTO, 
                                   payment_request_id: str, 
                                   expiry_time: datetime) -> AlipayPayRequestDTO:
        """Build Alipay+ Pay API request DTO"""
        order = request_dto.order
        
        # Get merchant info
        merchant_info = self._get_merchant_info(order.merchantId)
        
        return AlipayPayRequestDTO(
            paymentRequestId=payment_request_id,
            paymentAmount=order.orderAmount,
            paymentMethod=PaymentMethodDTO(paymentMethodType="CONNECT_WALLET"),
            paymentFactor=order.paymentFactor.model_dump(exclude_none=True) if order.paymentFactor else None,
            paymentExpiryTime=expiry_time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
            order=AlipayOrderDTO(
                referenceOrderId=order.referenceOrderId,
                orderDescription=order.orderDescription,
                orderAmount=order.orderAmount,
                merchant=merchant_info,
                goods=[g.model_dump(exclude_none=True) for g in order.goods] if order.goods else None,
                shipping=order.shipping.model_dump(exclude_none=True) if order.shipping else None,
                buyer=order.buyer.model_dump(exclude_none=True) if order.buyer else None,
                env=order.env.model_dump(exclude_none=True) if order.env else None
            )
        )
    
    def _get_merchant_info(self, merchant_id: str) -> Optional[MerchantInfoDTO]:
        """Get merchant info from database"""
        try:
            merchant = Merchant.objects.get(merchantId=merchant_id)
            return MerchantInfoDTO(
                referenceMerchantId=merchant.referenceMerchantId or None,
                merchantName=merchant.merchantName or None,
                merchantDisplayName=merchant.merchantDisplayName or None,
                merchantMCC=merchant.merchantMCC or None,
                merchantAddress=merchant.merchantAddress or None
            )
        except Merchant.DoesNotExist:
            return None
    
    def _handle_payment_in_process(self, payment_request_id: str, alipay_client: AlipayClient) -> PaymentResponseDTO:
        """Handle PAYMENT_IN_PROCESS with inquiry retry"""
        intervals = [2, 2, 3, 3, 5, 5, 10, 10, 10, 10]
        
        inquiry_dto = InquiryPaymentRequestDTO(paymentRequestId=payment_request_id)
        
        def inquiry():
            return alipay_client.inquiry_payment(inquiry_dto)
        
        def should_stop(response):
            result = response.result
            return result.resultStatus != 'U' or result.resultCode != 'UNKNOWN_EXCEPTION'
        
        return RetryHandler.retry_with_intervals(inquiry, intervals, should_stop)
    
    def _save_payment_request(self, request_dto: AlipayPayRequestDTO, 
                              response_dto: PaymentResponseDTO, 
                              payment_request_id: str):
        """Save payment request to database"""
        try:
            PaymentRequest.objects.create(
                paymentRequestId=payment_request_id,
                acquirerId=response_dto.acquirerId or '',
                paymentAmountValue=request_dto.paymentAmount.value,
                paymentAmountCurrency=request_dto.paymentAmount.currency,
                paymentMethodType=request_dto.paymentMethod.paymentMethodType,
                paymentExpiryTime=request_dto.paymentExpiryTime,
                paymentId=response_dto.paymentId or '',
                paymentTime=response_dto.paymentTime,
                pspId=response_dto.pspId or '',
                walletBrandName=response_dto.walletBrandName or '',
                mppPaymentId=response_dto.mppPaymentId or ''
            )
        except Exception as e:
            logger.error(f"Failed to save payment request: {e}")


class CancelPaymentView(APIView):
    """
    POST /api/cancel-payment
    Cancel a payment
    """
    
    def post(self, request):
        # Parse and validate request using DTO
        try:
            request_dto = CancelPaymentRequestDTO(**request.data)
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
        
        # Call Alipay+ cancelPayment API
        response_dto = alipay_client.cancel_payment(request_dto)
        
        # Log API record
        ApiRecord.objects.create(
            api_url='/aps/api/v1/payments/cancelPayment',
            request_body=request_dto.model_dump_json(),
            response_body=response_dto.model_dump_json(),
            message_type='OUTBOUND'
        )
        
        # Handle UNKNOWN_EXCEPTION with retry
        result = response_dto.result
        if result.resultStatus == 'U' and result.resultCode == 'UNKNOWN_EXCEPTION':
            response_dto = self._retry_cancel(request_dto, alipay_client)
        
        return Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK)
    
    def _retry_cancel(self, request_dto: CancelPaymentRequestDTO, alipay_client: AlipayClient) -> CancelPaymentResponseDTO:
        """Retry cancel for UNKNOWN_EXCEPTION"""
        def cancel():
            return alipay_client.cancel_payment(request_dto)
        
        def should_stop(response):
            result = response.result
            return result.resultStatus != 'U' or result.resultCode != 'UNKNOWN_EXCEPTION'
        
        return RetryHandler.retry_until_timeout(cancel, 10, 60, should_stop)


class InquiryPaymentView(APIView):
    """
    POST /api/inquiryPayment
    Query payment result
    """
    
    def post(self, request):
        # Parse and validate request using DTO
        try:
            request_dto = InquiryPaymentRequestDTO(**request.data)
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
        
        # Call Alipay+ inquiryPayment API
        response_dto = alipay_client.inquiry_payment(request_dto)
        
        # Log API record
        ApiRecord.objects.create(
            api_url='/aps/api/v1/payments/inquiryPayment',
            request_body=request_dto.model_dump_json(),
            response_body=response_dto.model_dump_json(),
            message_type='OUTBOUND'
        )
        
        # Handle UNKNOWN_EXCEPTION with retry
        result = response_dto.result
        if result.resultStatus == 'U' and result.resultCode == 'UNKNOWN_EXCEPTION':
            response_dto = self._handle_inquiry_retry(request_dto, alipay_client)
        
        return Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK)
    
    def _handle_inquiry_retry(self, request_dto: InquiryPaymentRequestDTO, alipay_client: AlipayClient) -> InquiryPaymentResponseDTO:
        """Handle inquiry retry with automatic cancel on expiry"""
        # Get payment request to check expiry time
        try:
            payment_request = PaymentRequest.objects.get(paymentRequestId=request_dto.paymentRequestId)
            # Use stored expiry time or default to 1 minute from now
            expiry_time = payment_request.paymentExpiryTime or (datetime.now(timezone.utc) + timedelta(minutes=1))
        except PaymentRequest.DoesNotExist:
            expiry_time = datetime.now(timezone.utc) + timedelta(minutes=1)
        
        def inquiry():
            return alipay_client.inquiry_payment(request_dto)
        
        def should_stop(response):
            result = response.result
            if result.resultStatus != 'U':
                return True
            # Check if expired
            if datetime.now(timezone.utc) > expiry_time:
                return True
            return False
        
        response_dto = RetryHandler.retry_until_timeout(inquiry, 5, 60, should_stop)
        
        # If still unknown after expiry, trigger cancel
        result = response_dto.result
        if result.resultStatus == 'U' and datetime.now(timezone.utc) > expiry_time:
            # Get paymentId from the response or use empty string
            payment_id = response_dto.paymentId or ''
            cancel_dto = CancelPaymentRequestDTO(
                paymentId=payment_id,
                paymentRequestId=request_dto.paymentRequestId
            )
            cancel_response = alipay_client.cancel_payment(cancel_dto)
            ApiRecord.objects.create(
                api_url='/aps/api/v1/payments/cancelPayment',
                request_body=cancel_dto.model_dump_json(),
                response_body=cancel_response.model_dump_json(),
                message_type='OUTBOUND'
            )
        
        return response_dto


@method_decorator(csrf_exempt, name='dispatch')
class NotifyPaymentView(APIView):
    """
    POST /alipay/notifyPayment
    Receive payment notification from Alipay+
    """
    authentication_classes = []  # No authentication for Alipay+ callback
    permission_classes = []
    
    def post(self, request):
        # Get service instances
        signature_service, _ = get_service_instances()
        
        # Verify signature
        signature_header = request.headers.get('Signature', '')
        request_time = request.headers.get('Request-Time', '')
        
        signature = signature_service.extract_signature_from_header(signature_header)
        
        is_valid = signature_service.verify_signature(
            'POST',
            '/alipay/notifyPayment',
            request_time,
            request.body.decode('utf-8'),
            signature
        )
        
        if not is_valid:
            logger.warning("Invalid signature in notifyPayment")
            response_dto = NotifyPaymentResponseDTO(
                result=ResultDTO(
                    resultCode='INVALID_SIGNATURE',
                    resultStatus='F',
                    resultMessage='Signature verification failed'
                )
            )
            return Response(response_dto.model_dump(), status=status.HTTP_200_OK)
        
        # Log API record
        ApiRecord.objects.create(
            api_url='/alipay/notifyPayment',
            request_body=request.body.decode('utf-8'),
            response_body='',
            message_type='INBOUND'
        )
        
        # Process notification
        notification_data = request.data
        payment_request_id = notification_data.get('paymentRequestId')
        
        # Update payment request
        try:
            payment_request = PaymentRequest.objects.get(paymentRequestId=payment_request_id)
            payment_request.paymentId = notification_data.get('paymentId', '')
            payment_request.paymentTime = notification_data.get('paymentTime')
            payment_request.pspId = notification_data.get('pspId', '')
            payment_request.walletBrandName = notification_data.get('walletBrandName', '')
            payment_request.mppPaymentId = notification_data.get('mppPaymentId', '')
            payment_request.save()
            
            # Save payment result
            payment_result = notification_data.get('paymentResult', {})
            PaymentRequestResult.objects.create(
                paymentRequestId=payment_request_id,
                isFinalStatus=True,
                resultStatus=payment_result.get('resultStatus', ''),
                resultCode=payment_result.get('resultCode', ''),
                resultMessage=payment_result.get('resultMessage', '')
            )
            
            # Save settlement if present
            settlement_amount = notification_data.get('settlementAmount', {})
            settlement_quote = notification_data.get('settlementQuote', {})
            
            if settlement_amount:
                Settlement.objects.create(
                    settlementId=str(uuid.uuid4()),
                    paymentRequestId=payment_request_id,
                    settlementAmount=settlement_amount.get('value', 0),
                    settlementCurrency=settlement_amount.get('currency', ''),
                    quoteId=settlement_quote.get('quoteId', ''),
                    quotePrice=settlement_quote.get('quotePrice'),
                    quoteCurrencyPair=settlement_quote.get('quoteCurrencyPair', ''),
                    quoteStartTime=settlement_quote.get('quoteStartTime'),
                    quoteExpiryTime=settlement_quote.get('quoteExpiryTime'),
                    quoteUnit=settlement_quote.get('quoteUnit', ''),
                    baseCurrency=settlement_quote.get('baseCurrency', '')
                )
        except PaymentRequest.DoesNotExist:
            logger.warning(f"Payment request not found: {payment_request_id}")
        
        response_dto = NotifyPaymentResponseDTO(
            result=ResultDTO(
                resultCode='SUCCESS',
                resultStatus='S',
                resultMessage='Notification processed successfully'
            )
        )
        return Response(response_dto.model_dump(), status=status.HTTP_200_OK)
