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
from apps.orders.orders_models import *
from .payments_models import PaymentRequest,  Settlement
from apps.api_records.api_records_models import ApiRecord
from apps.merchants.merchants_models import Merchant
from urllib.parse import urlparse, parse_qs
from dtos.request import *
from dtos.response import *
from rest_framework.test import APIRequestFactory
from utils.constants import Result,MessageType,HTTPMethod,PaymentStatus,ResultStatus
from utils.helpers import format_str_to_datetime
from utils.exceptions import SuperPayACQPException
from services.alipay_client import AlipayClient, RetryHandler
from services.signature_service import SignatureService
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

class PlaceOrderView(APIView):
    """
    POST /api/place-order
    Place an order and initiate payment
    """
    authentication_classes = []  # Use JWT middleware for auth
    permission_classes = []  # Permission handled by middleware

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
            if (isInStorePayment or (not isInStorePayment and isCashierPayment)):
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
            paymentFactor=request_dto.paymentFactor,
            paymentExpiryTime=expiry_time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
            paymentRedirectUrl="https://superpayacqp.onrender.com/payment-result?paymentRequestId="+payment_request_id,
            paymentNotifyUrl="https://superpayacqp.onrender.com/alipay/notifyPayment",
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
            paymentExpireTime=request_dto.paymentExpiryTime,
            paymentUrl=response_dto.paymentUrl,
            schemeUrl=response_dto.schemeUrl,
            applinkUrl=response_dto.applinkUrl,
            normalUrl=response_dto.normalUrl,
            appIdentifier=response_dto.appIdentifier

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
    authentication_classes = []  # Use JWT middleware for auth
    permission_classes = []  # Permission handled by middleware

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
    authentication_classes = []  # Use JWT middleware for auth
    permission_classes = []  # Permission handled by middleware

    def post(self, request):
        # Parse and validate request using DTO
        request_dto = self._validate_request(request)
        if isinstance(request_dto, Response):
            return request_dto

        # Get service instances
        _, alipay_client, db_service = get_service_instances()

        try:
            # Get payment request from database
            payment_request = self._get_payment_request(request_dto)
            if not payment_request:
                return self._error_response(request_dto, db_service,
                    f"Payment request not found for paymentRequestId: {request_dto.paymentRequestId} or paymentId: {request_dto.paymentId}")

            # Check if payment is still pending
            if self._is_payment_pending_or_expired(payment_request):
                # Query Alipay+ for latest status
                response_dto = self._query_alipay_status(request_dto, alipay_client, db_service)
            else:
                # Return cached status from database
                response_dto = db_service.buildInquiryPaymentResponseFromDB(payment_request)

            db_service.createApiRecordsWithReqRes('/api/inquiryPayment', HTTPMethod.POST, request_dto, response_dto, MessageType.INBOUND)
            return Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK)

        except Exception as e:
            logger.warning(f"Error: {e}")
            return self._error_response(request_dto, db_service, str(e))

    def _call_cancel_internal(self, request_dto: CancelPaymentRequestDTO) -> dict:
        """Call cancel payment internally using fabricated request"""
        factory = APIRequestFactory()
        request = factory.post('/api/cancel-payment', request_dto.model_dump(exclude_none=True), format='json')

        view = CancelPaymentView.as_view()
        response = view(request)

        # Type cast to access .data attribute (DRF Response has this attribute)
        if isinstance(response, Response):
            return response.data or {}
        return {}

    def _validate_request(self, request) -> InquiryPaymentRequestDTO | Response:
        """Validate and parse request DTO"""
        try:
            return InquiryPaymentRequestDTO(**request.data)
        except Exception as e:
            logger.warning(f"Invalid request: {e}")
            return Response({
                'result': {
                    'resultCode': 'INVALID_REQUEST',
                    'resultStatus': 'F',
                    'resultMessage': str(e)
                }
            }, status=status.HTTP_400_BAD_REQUEST)

    def _get_payment_request(self, request_dto: InquiryPaymentRequestDTO) -> PaymentRequest | None:
        """Get payment request from database by paymentRequestId or paymentId"""
        if request_dto.paymentRequestId:
            return PaymentRequest.objects.filter(paymentRequestId=request_dto.paymentRequestId).first()
        else:
            return PaymentRequest.objects.filter(paymentId=request_dto.paymentId).first()

    def _is_payment_pending_or_expired(self, payment_request: PaymentRequest) -> bool:
        """Check if payment is still in pending state"""
        return payment_request.resultStatus == 'U' and payment_request.paymentStatus == PaymentStatus.PENDING

    def _query_alipay_status(self, request_dto: InquiryPaymentRequestDTO,
                              alipay_client: AlipayClient,
                              db_service: DbService) -> InquiryPaymentResponseDTO:
        """Query Alipay+ for payment status with retry logic"""
        while True:
            response_dto = alipay_client.inquiry_payment(request_dto)
            db_service.createApiRecordsWithReqRes('/aps/api/v1/payments/inquiryPayment',
                                                   HTTPMethod.POST, request_dto, response_dto, MessageType.OUTBOUND)

            result = response_dto.result

            # Check if we got a final result
            if result.resultStatus == ResultStatus.SUCCESS and response_dto.paymentResult:
                payment_result = response_dto.paymentResult
                if payment_result.resultStatus in (ResultStatus.SUCCESS, ResultStatus.FAILURE):
                    db_service.updatePaymentRequestResultByInquiryPayment(request_dto, response_dto)
                    return response_dto
                if payment_result.resultStatus ==ResultStatus.UNKNOWN:
                    return self._handle_inquiry_retry(request_dto, alipay_client, db_service)
            # Handle UNKNOWN_EXCEPTION with retry handler
            elif result.resultStatus == ResultStatus.UNKNOWN and result.resultCode == 'UNKNOWN_EXCEPTION':
                return self._handle_inquiry_retry(request_dto, alipay_client, db_service)

            elif result.resultStatus==ResultStatus.FAILURE and result.resultCode=='ORDER_NOT_EXIST':
                self._call_cancel_internal(
                    CancelPaymentRequestDTO(paymentId=request_dto.paymentId, paymentRequestId=request_dto.paymentRequestId)
                )
                payment_request=self._get_payment_request(request_dto)
                if payment_request:
                    return db_service.buildInquiryPaymentResponseFromDB(payment_request)
                else:
                    return response_dto
            else:
                return response_dto


    def _error_response(self, request_dto: InquiryPaymentRequestDTO,
                        db_service: DbService,
                        error_message: str) -> Response:
        """Create error response"""
        result = Result.returnProcessFail()
        response_dto = InquiryPaymentResponseDTO(result=result)
        db_service.createApiRecordsWithReqRes('/api/inquiryPayment', HTTPMethod.POST, request_dto, response_dto, MessageType.INBOUND)
        return Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK)

    def _handle_inquiry_retry(self, request_dto: InquiryPaymentRequestDTO,
                               alipay_client: AlipayClient,
                               db_service: DbService) -> InquiryPaymentResponseDTO:
        """Handle inquiry retry with automatic cancel on expiry"""
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

        try:
            payment_request = PaymentRequest.objects.get(paymentRequestId=request_dto.paymentRequestId)
            # Use stored expiry time or default to 1 minute from now
            expiry_time = payment_request.paymentExpiryTime or (datetime.now(timezone.utc) + timedelta(minutes=1))
        except PaymentRequest.DoesNotExist:
            expiry_time = datetime.now(timezone.utc) + timedelta(minutes=1)

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
            db_service.createApiRecordsWithReqRes('/aps/api/v1/payments/cancelPayment', HTTPMethod.POST, cancel_dto, cancel_response, MessageType.OUTBOUND)
        if result.resultStatus == 'S':
            if response_dto.paymentResult.resultStatus=='S' or response_dto.paymentResult.resultStatus=='F':
                db_service.updatePaymentRequestResultByInquiryPayment(request_dto, response_dto)
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
            db_service.updatePaymentRequestResultByNotifyPayment(notification_dto=notification_dto,payment_request_id=payment_request_id)


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

@method_decorator(csrf_exempt, name='dispatch')
class ConsultPaymentView(APIView):
    authentication_classes = []  # Use JWT middleware for auth
    permission_classes = []  # Permission handled by middleware

    def post(self, request):
        try:
            request_dto = AlipayConsultPaymentRequestDTO(**request.data)
        except Exception as e:
            logger.warning(f"Invalid request: {e}")
            return Response({
                'result': {
                    'resultCode': 'INVALID_REQUEST',
                    'resultStatus': 'F',
                    'resultMessage': str(e)
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        _, alipay_client, db_service = get_service_instances()
        if not request_dto.settlementStrategy:
            request_dto.settlementStrategy=SettlementStrategyDTO(
                settlementCurrency="MYR"
            )

        try:
            response_dto = alipay_client.consultPayment(request_dto)
            db_service.createApiRecordsWithReqRes('/api/consult-payment',HTTPMethod.POST,request_dto,response_dto,MessageType.INBOUND)
            return Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK)

        except Exception as e:
            result = Result.returnProcessFail()
            response_dto=PaymentResponseDTO(result=result)
            db_service.createApiRecordsWithReqRes('/api/consult-payment',HTTPMethod.POST,request_dto,response_dto,MessageType.INBOUND)
            return Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class PrivatePlaceOrderCodeView(APIView):
    authentication_classes = []  # Disable DRF authentication, JWT handled by middleware
    def post(self, request):
        try:
            request_dto=PrivatePlaceOrderRequestDTO(**request.data)
        except Exception as e:
            logger.warning(f"Invalid request: {e}")
            return Response({
                'result': {
                    'resultCode': 'INVALID_REQUEST',
                    'resultStatus': 'F',
                    'resultMessage': str(e)
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        signature_service, alipay_client, db_service = get_service_instances()

        try:
            payment_request=db_service.savePrivatePlaceOrder(request_dto)
            response_dto=PrivatePlaceOrderResponseDTO(
                result=Result.returnSuccess(),
                paymentRequestId=payment_request.paymentRequestId,
                paymentExpireTime=payment_request.paymentExpiryTime.strftime("%Y-%m-%dT%H:%M:%S+08:00") if payment_request.paymentExpiryTime else '',
                paymentAmount=AmountDTO(
                    value=payment_request.paymentAmountValue,
                    currency=payment_request.paymentAmountCurrency
                ),
                codeValue="https://superpayacqp.onrender.com/private-order-code?paymentRequestId="+payment_request.paymentRequestId
            )
            db_service.createApiRecordsWithReqRes('/api/private-place-order',HTTPMethod.POST,request_dto,response_dto,MessageType.INBOUND)
            return Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK)
        except Exception as e:
            logger.warning(f"Error: {e}")
            result = Result.returnProcessFail()
            response_dto=PrivatePlaceOrderResponseDTO(result=result)
            db_service.createApiRecordsWithReqRes('/api/private-place-order',HTTPMethod.POST,request_dto,response_dto,MessageType.INBOUND)
            return Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class UserInitiatedPayView(APIView):
    authentication_classes = []  # Disable DRF authentication for Alipay callback
    
    def buildAlipayUserInitiatedPayResponse (self,db_service: DbService,payment_request_object:PaymentRequest) -> AlipayUserInitiatedPayResponseDTO:
            order_record=Order.objects.filter(paymentRequestId=payment_request_object.paymentRequestId).first()
            if order_record:
                if not order_record.orderAmountValue :
                    raise ValueError("orderAmountValue is required")
                if not order_record.merchantId:
                    raise ValueError("merchantId is required")
                
                merchant_record=db_service.getMerchantInfo(order_record.merchantId)
                good_records=OrderGoods.objects.filter(orderId=order_record.referenceOrderId).all()
                goods=[]
                for g in good_records:
                    if g.goodsUnitAmountValue:
                        temp=GoodsDTO(
                            referenceGoodsId=g.referenceGoodsId,
                            goodsName=g.goodsName,
                            goodsCategory=g.goodsCategory,
                            goodsBrand=g.goodsBrand,
                            goodsUnitAmount=AmountDTO(currency=g.goodsUnitAmountCurrency,value=g.goodsUnitAmountValue),
                            goodsQuantity=g.goodsQuantity
                        )
                        goods.append(temp)
                
                order=AlipayOrderDTO(
                    referenceOrderId=order_record.referenceOrderId,
                    orderDescription=order_record.orderDescription,
                    orderAmount=AmountDTO(currency=order_record.orderAmountCurrency,value=order_record.orderAmountValue),
                    goods=goods,
                    shipping=ShippingDTO(
                        shippingName=order_record.shippingName,
                        shippingPhoneNo=order_record.shippingPhoneNo,
                        shippingAddress=order_record.shippingAddress,
                        shippingCarrier=order_record.shippingCarrier
                    ),
                    buyer=BuyerDTO(
                        referenceBuyerId=order_record.referenceBuyerId,
                        buyerName=order_record.buyerName,
                        buyerPhoneNo=order_record.buyerPhoneNo,
                        buyerEmail=order_record.buyerEmail
                    ),
                    env=order_record.env,

                )
            else:
                order=None

            # Handle paymentExpiryTime - could be datetime or string
            payment_expiry_time_str = None
            if payment_request_object.paymentExpiryTime:
                if isinstance(payment_request_object.paymentExpiryTime, str):
                    payment_expiry_time_str = payment_request_object.paymentExpiryTime
                else:
                    payment_expiry_time_str = payment_request_object.paymentExpiryTime.strftime("%Y-%m-%dT%H:%M:%S+08:00")
            
            # Handle settlementStrategy - could be dict or string
            settlement_currency = 'MYR'
            if payment_request_object.settlementStrategy:
                if isinstance(payment_request_object.settlementStrategy, dict):
                    settlement_currency = payment_request_object.settlementStrategy.get('settlementCurrency', 'MYR')
                elif isinstance(payment_request_object.settlementStrategy, str):
                    settlement_currency = payment_request_object.settlementStrategy

            return AlipayUserInitiatedPayResponseDTO(
                    result=Result.returnSuccess(),
                    codeType=payment_request_object.inStorePaymentScenario,
                    paymentRequestId=payment_request_object.paymentRequestId,
                    paymentFactor=PaymentFactorDTO(
                        isInStorePayment=payment_request_object.isInStorePayment,
                        isCashierPayment=payment_request_object.isCashierPayment,
                        inStorePaymentScenario=payment_request_object.inStorePaymentScenario
                    ),
                    order=order,
                    paymentAmount=AmountDTO(
                        currency=payment_request_object.paymentAmountCurrency,
                        value=payment_request_object.paymentAmountValue
                    ),
                    paymentNotifyUrl=payment_request_object.paymentNotifyUrl or '',
                    paymentRedirectUrl=payment_request_object.paymentRedirectUrl,
                    paymentExpiryTime=payment_expiry_time_str,
                    settlementStrategy=SettlementStrategyDTO(
                        settlementCurrency=settlement_currency
                    ),
                    splitSettlementId=payment_request_object.splitSettlementId
                )
    def post(self, request):
        signature_service, alipay_service,db_service= get_service_instances()
        raw_body = request.body.decode('utf-8')
        signature_header = request.headers.get('Signature', '')
        request_time = request.headers.get('Request-Time', '')
        signature = signature_service.extract_signature_from_header(signature_header)
        if signature:
            is_valid = signature_service.verify_signature(
                'POST',
                '/alipay/userInitiatedPay',
                request_time,
                raw_body,
                signature
            )
            if not is_valid:
                logger.warning("Invalid signature in userInitiatedPay")
                result = Result.returnInvalidSignature()
                response_dto = AlipayUserInitiatedPayResponseDTO(
                    result=result,
                    paymentNotifyUrl=os.getenv('NOTIFY_PAYMENT_URL', 'https://superpayacqp.onrender.com/alipay/notifyPayment')
                )
                response_header=alipay_service._make_response_header("POST",'/alipay/userInitiatedPay',response_dto.model_dump(exclude_none=True))
                db_service.createApiRecordsWithReqRes('/alipay/userInitiatedPay',HTTPMethod.POST,request.data,response_dto,MessageType.INBOUND)
                return Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK,headers=response_header)
        else:
            result = Result.returnInvalidSignature()
            response_dto = AlipayUserInitiatedPayResponseDTO(
                    result=result,
                    paymentNotifyUrl=os.getenv('NOTIFY_PAYMENT_URL', 'https://superpayacqp.onrender.com/alipay/notifyPayment')
                )
            response_header=alipay_service._make_response_header("POST",'/alipay/userInitiatedPay',response_dto.model_dump(exclude_none=True))
            db_service.createApiRecordsWithReqRes('/alipay/userInitiatedPay',HTTPMethod.POST,request.data,response_dto,MessageType.INBOUND)
            return Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK,headers=response_header)

        
        try:
            notification_dto = AlipayUserInitiatedPayRequestDTO(**request.data)
            parsed = urlparse(notification_dto.codeValue)
            query_params = parse_qs(parsed.query)
            payment_request_id=query_params.get("paymentRequestId", [None])[0]
            payment_request_object=PaymentRequest.objects.filter(paymentRequestId=payment_request_id).first()
            if payment_request_object:
                # Check if order is closed
                if payment_request_object.resultStatus=='F' and payment_request_object.resultCode=='ORDER_IS_CLOSED':
                    response_dto=AlipayUserInitiatedPayResponseDTO(
                        result=Result.returnOrderIsClosed(),
                        paymentNotifyUrl=os.getenv('NOTIFY_PAYMENT_URL', 'https://superpayacqp.onrender.com/alipay/notifyPayment')
                    )
                    response_header=alipay_service._make_response_header("POST",'/alipay/userInitiatedPay',response_dto.model_dump(exclude_none=True))
                    db_service.createApiRecordsWithReqRes('/alipay/userInitiatedPay',HTTPMethod.POST,request.data,response_dto,MessageType.INBOUND)
                    return Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK,headers=response_header)
                
                # Check if code is expired - use timezone-aware comparison
                expiry = payment_request_object.paymentExpiryTime
                if expiry is not None:
                    # Handle both datetime and string types
                    if isinstance(expiry, str):
                        expiry = format_str_to_datetime(expiry)
                    
                    if expiry and datetime.now(timezone.utc) > expiry:
                        response_dto = AlipayUserInitiatedPayResponseDTO(
                            result=Result.returnExpiredCode(),
                            paymentNotifyUrl=os.getenv('NOTIFY_PAYMENT_URL', 'https://superpayacqp.onrender.com/alipay/notifyPayment')
                        )
                        response_header=alipay_service._make_response_header("POST",'/alipay/userInitiatedPay',response_dto.model_dump(exclude_none=True))
                        db_service.createApiRecordsWithReqRes('/alipay/userInitiatedPay',HTTPMethod.POST,request.data,response_dto,MessageType.INBOUND)
                        return Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK,headers=response_header)
                
                # Update payment request with Alipay info
                payment_request_object.acquirerId=notification_dto.acquirerId
                payment_request_object.pspId=notification_dto.pspId
                payment_request_object.customerId=notification_dto.customerId
                payment_request_object.save()
                
                response_dto=self.buildAlipayUserInitiatedPayResponse(db_service,payment_request_object)
                response_header=alipay_service._make_response_header("POST",'/alipay/userInitiatedPay',response_dto.model_dump(exclude_none=True))
                db_service.createApiRecordsWithReqRes('/alipay/userInitiatedPay',HTTPMethod.POST,request.data,response_dto,MessageType.INBOUND)
                return Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK,headers=response_header)

            else:
                response_dto=AlipayUserInitiatedPayResponseDTO(
                    result=Result.returnInvalidCode(),
                    paymentNotifyUrl=os.getenv('NOTIFY_PAYMENT_URL', 'https://superpayacqp.onrender.com/alipay/notifyPayment')
                )
                response_header=alipay_service._make_response_header("POST",'/alipay/userInitiatedPay',response_dto.model_dump(exclude_none=True))
                db_service.createApiRecordsWithReqRes('/alipay/userInitiatedPay',HTTPMethod.POST,request.data,response_dto,MessageType.INBOUND)
                return Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK,headers=response_header)
        except Exception as e:
                logger.error(f"Error in userInitiatedPay: {e}")
                response_dto=AlipayUserInitiatedPayResponseDTO(
                    result=Result.returnUnknownException(),
                    paymentNotifyUrl=os.getenv('NOTIFY_PAYMENT_URL', 'https://superpayacqp.onrender.com/alipay/notifyPayment')
                )
                response_header=alipay_service._make_response_header("POST",'/alipay/userInitiatedPay',response_dto.model_dump(exclude_none=True))
                return Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK,headers=response_header)
