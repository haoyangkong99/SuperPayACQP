"""
Payment API Views
"""
import json
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import os
from .payments_models import PaymentRequest,  Settlement
from apps.api_records.api_records_models import ApiRecord
from apps.merchants.merchants_models import Merchant

from dtos.request import (
    PlaceOrderRequestDTO, 
    CancelPaymentRequestDTO, 
    InquiryPaymentRequestDTO
)
from dtos.request import (
    AlipayPayRequestDTO, 
    PaymentMethodDTO, 
    AlipayOrderDTO,
    MerchantInfoDTO,
    NotifyPaymentRequestDTO,
    GoodsDTO,
    SettlementStrategyDTO,
    AlipayAmountDTO,
    AlipayPaymentFactorDTO
)
from dtos.response import (
    PaymentResponseDTO, 
    CancelPaymentResponseDTO, 
    InquiryPaymentResponseDTO,
    NotifyPaymentResponseDTO,
    BaseResponseDTO,
    AlipayPayResponseDTO
)

from utils.constants import Result,MessageType,HTTPMethod
from utils.helpers import format_str_to_datetime
from services.alipay_client import AlipayClient, RetryHandler
from services.signature_service import SignatureService
from services.db_service import DbService
from .tasks import handle_payment_in_process_task

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
        
        # Calculate expiry time (current time + 1 minute in UTC+8 timezone)
        
        malaysia_tz = ZoneInfo("Asia/Kuala_Lumpur")
        expiry_time=datetime.now(malaysia_tz)
        # Get service instances
        signature_service, alipay_client, db_service = get_service_instances()
        isInStorePayment=request_dto.paymentFactor.isInStorePayment
        isCashierPayment=request_dto.paymentFactor.isCashierPayment
        try:
            if (isInStorePayment):
                if isCashierPayment:
                    expiry_time =  expiry_time+ timedelta(minutes=3)
                else:
                    expiry_time = expiry_time + timedelta(minutes=1)
                alipay_request_dto = self._build_alipay_request_dto(
                    request_dto, 
                    payment_request_id, 
                    expiry_time
                )
            # Call Alipay+ Pay API
                alipay_response_dto = alipay_client.pay(alipay_request_dto)
                response_dto=self._map_AlipayPayResponseDTO_to_PaymentResponseDTO(alipay_request_dto,alipay_response_dto)  
            # Log API record
                db_service.createApiRecordsWithReqRes('/aps/api/v1/payments/pay',HTTPMethod.POST,alipay_request_dto,alipay_response_dto,MessageType.OUTBOUND)
            
            # Process result
                result = alipay_response_dto.result
                result_status = result.resultStatus
                result_code = result.resultCode
            
            # Save payment request to database FIRST (before spawning background task)
                db_service.savePaymentRequest(alipay_request_dto, alipay_response_dto, payment_request_id)
            
            # Handle PAYMENT_IN_PROCESS with background task
                # if result_status == 'U' and result_code == 'PAYMENT_IN_PROCESS':
                #     # Spawn background task to handle retry
                #     handle_payment_in_process_task(payment_request_id)
                #     logger.info(f"Spawned background task for PAYMENT_IN_PROCESS: {payment_request_id}")
                
            # Handle UNKNOWN_EXCEPTION with retry
                if result_status == 'U' and result_code == 'UNKNOWN_EXCEPTION':
                    alipay_response_dto = alipay_client.pay(alipay_request_dto)
                    response_dto=self._map_AlipayPayResponseDTO_to_PaymentResponseDTO(alipay_request_dto,alipay_response_dto)  
            else:
                result = Result.returnProcessFail()
                response_dto=PaymentResponseDTO(
                        result=result) 
        
            db_service.createApiRecordsWithReqRes('/api/place-order',HTTPMethod.POST,request_dto,response_dto,MessageType.INBOUND)    
            return Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK)

        except Exception as e:
            logger.warning(f"Error: {e}")
            result = Result.returnProcessFail()
            response_dto=PaymentResponseDTO(result=result)
            db_service.createApiRecordsWithReqRes('/api/place-order',HTTPMethod.POST,request_dto,response_dto,MessageType.INBOUND)    
            return Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK)
 
    def _build_alipay_request_dto(self, request_dto: PlaceOrderRequestDTO, 
                                   payment_request_id: str, 
                                   expiry_time: datetime) -> AlipayPayRequestDTO:
        """Build Alipay+ Pay API request DTO"""
        order = request_dto.order
        
        # Get merchant info
        _,_,db_service=get_service_instances()
        merchant_info = db_service.getMerchantInfo(merchant_id=order.merchantId)
        logger.debug(f"merchant info: {merchant_info}")
        return AlipayPayRequestDTO(
            paymentRequestId=payment_request_id,
            paymentAmount=AlipayAmountDTO(
                currency=request_dto.paymentAmount.currency,
                value=str(request_dto.paymentAmount.value)
            ),
            paymentMethod=request_dto.paymentMethod,
            paymentFactor=AlipayPaymentFactorDTO(
                isInStorePayment="true" if request_dto.paymentFactor.isInStorePayment else "false",
                isCashierPayment="true" if request_dto.paymentFactor.isCashierPayment else "false",
                inStorePaymentScenario=request_dto.paymentFactor.inStorePaymentScenario
            ),
            paymentExpiryTime=expiry_time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
            paymentRedirectUrl="https://superpayacqp-production.up.railway.app/payment-result?paymentRequestId="+payment_request_id,
            paymentNotifyUrl="https://superpayacqp-production.up.railway.app/alipay/notifyPayment",
            order=AlipayOrderDTO(
                referenceOrderId=order.referenceOrderId if order.referenceOrderId else str(uuid.uuid4()),
                orderDescription=order.orderDescription,
                orderAmount=order.orderAmount,
                merchant=merchant_info,
                goods=[GoodsDTO(
                    referenceGoodsId=g.referenceGoodsId,
                    goodsName=g.goodsName,
                    goodsCategory=g.goodsCategory,
                    goodsUnitAmount=g.goodsUnitAmount,
                    goodsQuantity=g.goodsQuantity,
                    goodsBrand=g.goodsBrand
                ) for g in order.goods] if order.goods else None,
                shipping=order.shipping,
                buyer=order.buyer,
                env=order.env
            ),
            settlementStrategy=SettlementStrategyDTO(
                settlementCurrency='MYR'
            ) if request_dto.paymentAmount.currency !='MYR' else None
        )
    def _map_AlipayPayResponseDTO_to_PaymentResponseDTO(self, request_dto: AlipayPayRequestDTO, response_dto: AlipayPayResponseDTO) -> PaymentResponseDTO:
        return PaymentResponseDTO(
            result=response_dto.result,
            paymentRequestId=request_dto.paymentRequestId,
            paymentId=response_dto.paymentId,
            paymentTime=response_dto.paymentTime,
            paymentAmount=response_dto.paymentAmount,
            customerId=response_dto.customerId,
            pspId=response_dto.pspId,
            walletBrandName=response_dto.walletBrandName,
            mppPaymentId=response_dto.mppPaymentId,
            orderCodeForm=response_dto.orderCodeForm,
            paymentExpireTime=request_dto.paymentExpiryTime
        )
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
        
        # Validate that at least one identifier is provided
        if not request_dto.paymentRequestId and not request_dto.paymentId:
            return Response({
                'result': {
                    'resultCode': 'INVALID_REQUEST',
                    'resultStatus': 'F',
                    'resultMessage': 'Either paymentRequestId or paymentId is required'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        signature_service, alipay_client, db_service = get_service_instances()
        try:
            # If paymentId is not provided, fetch it from database
            if not request_dto.paymentId and request_dto.paymentRequestId:
                payment_request = PaymentRequest.objects.filter(paymentRequestId=request_dto.paymentRequestId).first()
                if payment_request and payment_request.paymentId:
                    request_dto.paymentId = payment_request.paymentId
                else:
                    return Response( BaseResponseDTO(result=Result.returnOrderNotExist()).model_dump(exclude_none=True), status=status.HTTP_200_OK)
            
            # If paymentRequestId is not provided, fetch it from database
            if  request_dto.paymentId and not request_dto.paymentRequestId:
                payment_request = PaymentRequest.objects.filter(paymentId=request_dto.paymentId).first()
                if payment_request and payment_request.paymentRequestId:
                    request_dto.paymentRequestId = payment_request.paymentRequestId
                else:
                    return Response( BaseResponseDTO(result=Result.returnOrderNotExist()).model_dump(exclude_none=True), status=status.HTTP_200_OK)
            
            # Call Alipay+ cancelPayment API
            response_dto = alipay_client.cancel_payment(request_dto)

            # Log API record
            db_service.createApiRecordsWithReqRes('/aps/api/v1/payments/cancelPayment',HTTPMethod.POST,request_dto,response_dto,MessageType.OUTBOUND)
           
            # Handle UNKNOWN_EXCEPTION with retry
            result = response_dto.result

            if result.resultStatus == 'U' and result.resultCode == 'UNKNOWN_EXCEPTION':
                response_dto = self._retry_cancel(request_dto, alipay_client)
            if response_dto.result.resultStatus=='S' and request_dto.paymentRequestId:
                db_service.updatePaymentRequestResultByCancelled(request_dto.paymentRequestId,response_dto.result)
            
            db_service.createApiRecordsWithReqRes('/api/cancel-payment',HTTPMethod.POST,request_dto,response_dto,MessageType.INBOUND)    
            return Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK)
        except Exception as e:
            logger.warning(f"Error: {e}")
            result = Result.returnProcessFail()
            response_dto=PaymentResponseDTO(result=result)
            db_service.createApiRecordsWithReqRes('/api/cancel-payment',HTTPMethod.POST,request_dto,response_dto,MessageType.INBOUND)    
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
        signature_service, alipay_client, db_service = get_service_instances()
       
        try:
            # Call Alipay+ inquiryPayment API
            response_dto = alipay_client.inquiry_payment(request_dto)
        
            # Log API record
            db_service.createApiRecordsWithReqRes('/aps/api/v1/payments/inquiryPayment',HTTPMethod.POST,request_dto,response_dto,MessageType.OUTBOUND)

        # Handle UNKNOWN_EXCEPTION with retry
            result = response_dto.result
            if result.resultStatus =='S':
                db_service.updatePaymentRequestResultByInquiryPayment(response_dto)
            if result.resultStatus == 'U' and result.resultCode == 'UNKNOWN_EXCEPTION':
                response_dto = self._handle_inquiry_retry(request_dto, alipay_client,db_service)
            db_service.createApiRecordsWithReqRes('/api/inquiryPayment',HTTPMethod.POST,request_dto,response_dto,MessageType.INBOUND)   
            return Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK)

        except Exception as e:
            logger.warning(f"Error: {e}")
            result = Result.returnProcessFail()
            response_dto=InquiryPaymentResponseDTO(result=result)
            db_service.createApiRecordsWithReqRes('/api/inquiryPayment',HTTPMethod.POST,request_dto,response_dto,MessageType.INBOUND)    
            return Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK)

    
    def _handle_inquiry_retry(self, request_dto: InquiryPaymentRequestDTO, alipay_client: AlipayClient,db_service:DbService) -> InquiryPaymentResponseDTO:
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
            db_service.createApiRecordsWithReqRes('/aps/api/v1/payments/cancelPayment',HTTPMethod.POST,cancel_dto,cancel_response,MessageType.OUTBOUND)
        
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
        signature_service, alipay_service,db_service= get_service_instances()
        

        # Read raw body first for signature verification (must be done before accessing request.data)
        raw_body = request.body.decode('utf-8')

        
        # Verify signature
        signature_header = request.headers.get('Signature', '')
        request_time = request.headers.get('Request-Time', '')
        logger.debug(f"NotifyPayment - signature_header: {signature_header[:100]}...")
        logger.debug(f"NotifyPayment - request_time: {request_time}")
        signature = signature_service.extract_signature_from_header(signature_header)
        if signature:
            is_valid = signature_service.verify_signature(
                'POST',
                '/alipay/notifyPayment',
                request_time,
                raw_body,
                signature
            )
        
            if not is_valid:
                logger.warning("Invalid signature in notifyPayment")
                result = Result.returnInvalidSignature()
                response_dto = NotifyPaymentResponseDTO(
                    result=result
                )
                response_header=alipay_service._make_response_header("POST",'/alipay/notifyPayment',response_dto.model_dump(exclude_none=True))
                db_service.createApiRecordsWithReqRes('/alipay/notifyPayment',HTTPMethod.POST,request.data,response_dto,MessageType.INBOUND)
                return Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK,headers=response_header)
        
        else:
            logger.warning("Invalid signature in notifyPayment")
            result = Result.returnInvalidSignature()
            response_dto = NotifyPaymentResponseDTO(
                    result=result
                )
            response_header=alipay_service._make_response_header("POST",'/alipay/notifyPayment',response_dto.model_dump(exclude_none=True))
            db_service.createApiRecordsWithReqRes('/alipay/notifyPayment',HTTPMethod.POST,request.data,response_dto,MessageType.INBOUND)
            return Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK,headers=response_header)
        
        # Process notification
        notification_dto = NotifyPaymentRequestDTO(**request.data)
        payment_request_id = notification_dto.paymentRequestId
        
        # Update payment request
        try:
            payment_request = PaymentRequest.objects.get(paymentRequestId=payment_request_id)
            if notification_dto.paymentId:
                payment_request.paymentId = notification_dto.paymentId
            if notification_dto.paymentTime:
                payment_request.paymentTime = format_str_to_datetime(notification_dto.paymentTime)
            if notification_dto.pspId:
                payment_request.pspId = notification_dto.pspId
            if notification_dto.walletBrandName:
                payment_request.walletBrandName = notification_dto.walletBrandName
            if notification_dto.mppPaymentId:
                payment_request.mppPaymentId = notification_dto.mppPaymentId
            
            payment_request.resultStatus=notification_dto.paymentResult.resultStatus
            payment_request.resultCode=notification_dto.paymentResult.resultCode
            payment_request.resultMessage=notification_dto.paymentResult.resultMessage
            payment_request.save()
            

            # Save settlement if present
            settlementCheck=Settlement.objects.filter(paymentRequestId=payment_request_id).first()
            if not settlementCheck:
                settlement_amount = notification_dto.settlementAmount
                settlement_quote = notification_dto.settlementQuote
                if settlement_amount:
                    Settlement.objects.create(
                        settlementId=str(uuid.uuid4()),
                        paymentRequestId=payment_request_id,
                        settlementAmountValue=settlement_amount.value,
                        settlementCurrency=settlement_amount.currency or 'MYR',  # Default to MYR if not provided
                        quoteId=settlement_quote.quoteId if settlement_quote else None,
                        quotePrice=settlement_quote.quotePrice if settlement_quote else None,
                        quoteCurrencyPair=settlement_quote.quoteCurrencyPair if settlement_quote else None,
                        quoteStartTime=settlement_quote.quoteStartTime if settlement_quote else None,
                        quoteExpiryTime=settlement_quote.quoteExpiryTime if settlement_quote else None,
                        quoteUnit=settlement_quote.quoteUnit if settlement_quote else None,
                        baseCurrency=settlement_quote.baseCurrency if settlement_quote else None
                    )

        except PaymentRequest.DoesNotExist:
            logger.warning(f"Payment request not found: {payment_request_id}")
        
        result = Result.returnSuccess()
        response_dto = NotifyPaymentResponseDTO(
            result=result
        )
        response_header=alipay_service._make_response_header("POST",'/alipay/notifyPayment',response_dto.model_dump(exclude_none=True))
        db_service.createApiRecordsWithReqRes('/alipay/notifyPayment',HTTPMethod.POST,notification_dto.model_dump(exclude_none=True),response_dto,MessageType.INBOUND)
        notifyPaymentResponse=Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK,headers=response_header)
        
        logger.debug("response header for notifypayment: {notifyPaymentResponse.headers}")
        logger.debug("response body for notifypayment: {notifyPaymentResponse.data}")
        return notifyPaymentResponse
