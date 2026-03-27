import json
import logging
import uuid
import os
from datetime import datetime, timedelta, timezone as dt_timezone
from typing import Optional
from zoneinfo import ZoneInfo

from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.api_records.api_records_models import ApiRecord
from apps.merchants.merchants_models import Merchant, EntryCode
import requests as http_requests
from dtos.request import (
    AlipayPayRequestDTO, 
    PaymentMethodDTO, 
    AlipayOrderDTO,
    MerchantInfoDTO,
    PlaceOrderRequestDTO,
    AmountDTO,
    OrderDTO,
    PaymentFactorDTO,
    EnvDTO,
    EntryCodeConfirmRequestDTO,
    SettlementStrategyDTO,
    StoreDTO,
    AlipayAmountDTO,
    AlipayPaymentFactorDTO
)
from dtos.response import (
    BaseResponseDTO,
    EntryCodeConfirmResponseDTO
)
from django.utils import timezone

from utils.constants import Result,MessageType,HTTPMethod,ALLOWED_UA_IDENTIFIERS
from services.alipay_client import AlipayClient, RetryHandler
from services.signature_service import SignatureService
from services.db_service import DbService

logger = logging.getLogger(__name__)

# Shared service instances
_service_instances: Optional[tuple[SignatureService, AlipayClient, DbService]] = None

def get_service_instances() -> tuple[SignatureService, AlipayClient, DbService]:
    """Get signature service, Alipay client, and DB service instances"""
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




@method_decorator(csrf_exempt, name='dispatch')
class MerchantView(APIView):
    def post(self, request):
        try:
            request_dto = MerchantInfoDTO(**request.data)
        except Exception as e:
            logger.warning(f"Invalid request: {e}")
            return Response({
                'result': {
                    'resultCode': 'INVALID_REQUEST',
                    'resultStatus': 'F',
                    'resultMessage': str(e)
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            _,_,dbService=get_service_instances()
            dbService.createMerchants(request_dto)
            result = Result.returnSuccess()
            response=BaseResponseDTO(
                    result=result
                )
            dbService.createApiRecordsWithReqRes('/api/merchants',HTTPMethod.POST,request_dto,response,MessageType.INBOUND)
            return Response(response.model_dump(exclude_none=True), status=status.HTTP_200_OK)
        except Exception as e:
            logger.warning(f"error: {e}")
            result = Result.returnProcessFail()
            response=BaseResponseDTO(
                    result=result
                )
            return Response(response.model_dump(exclude_none=True), status=status.HTTP_200_OK)
        
@method_decorator(csrf_exempt, name='dispatch')
class MerchantDeleteView(APIView):
    def delete(self, request):
        merchant_id = request.query_params.get('merchantId')
        
        if not merchant_id:
            return Response({
                'error': 'merchantId is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            merchant = Merchant.objects.filter(merchantId=merchant_id).first()
            if not merchant:
                return Response({
                    'error': 'Merchant not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            merchant.delete()
            
            return Response({
                'message': 'Merchant deleted successfully',
                'merchantId': merchant_id
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error deleting merchant: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GenerateEntryCodeView(APIView):
    """
    POST /api/generate-entry-code
    Generate an entry code for a merchant
    """
    
    def post(self, request):
        # Get merchant ID from request body
        merchant_id = request.data.get('merchantId')
        
        if not merchant_id:
            return Response({
                'result': {
                    'resultCode': 'INVALID_REQUEST',
                    'resultStatus': 'F',
                    'resultMessage': 'merchantId is required'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify merchant exists
        merchant = Merchant.objects.filter(merchantId=merchant_id).first()
        if not merchant:
            return Response(BaseResponseDTO(result=Result.returnMerchantNotRegistered()), status=status.HTTP_200_OK)
        
        try:
            # Check if there's an active entry code for this merchant
            active_entry_code = EntryCode.objects.filter(
                merchantId=merchant_id,
                status='Active',
                codeExpireTime__gt=datetime.now(dt_timezone.utc)
            ).first()
            
            if active_entry_code:
                # Use existing active entry code
                code_id = active_entry_code.codeId
                logger.debug(f"Found active entry code for merchant {merchant_id}: {code_id}")
            else:
                # Create new entry code
                code_id = str(uuid.uuid4())
                current_time = datetime.now(dt_timezone.utc)
                # Set expiry time to 24 hours from now
                expiry_time = current_time + timedelta(days=365)
                
                # Deactivate any previous active entry codes for this merchant
                EntryCode.objects.filter(
                    merchantId=merchant_id,
                    status='Active'
                ).update(status='Inactive')
                
                # Create new entry code
                EntryCode.objects.create(
                    codeId=code_id,
                    merchantId=merchant_id,
                    codeStartTime=current_time,
                    codeExpireTime=expiry_time,
                    status='Active'
                )
   
            
            # Construct entry code URL
            base_url = os.getenv('API_BASE_URL')
            entry_code_url = f"{base_url}entry-code?merchantId={merchant_id}&codeId={code_id}"
            
            # Get the entry code record for timestamps
            entry_code_record = EntryCode.objects.filter(codeId=code_id).first()
            
            result = Result.returnSuccess()
            response = {
                'result': result.model_dump(),
                'entryCodeUrl': entry_code_url,
                'codeId': code_id,
                'codeStartTime': entry_code_record.codeStartTime.isoformat() if entry_code_record and entry_code_record.codeStartTime else None,
                'codeExpireTime': entry_code_record.codeExpireTime.isoformat() if entry_code_record and entry_code_record.codeExpireTime else None,
            }
            
            return Response(response, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error generating entry code: {e}")
            result = Result.returnProcessFail()
            return Response({
                'result': result.model_dump()
            }, status=status.HTTP_200_OK)


class EntryCodeView(APIView):
    """
    GET /entry-code
    Display the entry code payment page
    """
    
    def get(self, request):
        # Get merchantId and codeId from URL parameters
        merchant_id = request.GET.get('merchantId')
        code_id = request.GET.get('codeId')
        
        # Validate parameters
        if not merchant_id or not code_id:
            return render(request, 'entry_code.html', {
                'valid': False, 
                'error_message': 'Invalid link. Missing required parameters.'
            })
        
        # Check if entry code exists and is active
        entry_code = EntryCode.objects.filter(
            codeId=code_id,
            merchantId=merchant_id,
            status='Active'
        ).first()
        
        if not entry_code:
            return render(request, 'entry_code.html', {
                'valid': False, 
                'error_message': 'Invalid or expired entry code.'
            })
        
        # Check if entry code is expired
        from django.utils import timezone
        if entry_code.codeExpireTime < timezone.now():
            # Update status to Inactive
            entry_code.status = 'Inactive'
            entry_code.save()
            return render(request, 'entry_code.html', {
                'valid': False, 
                'error_message': 'Entry code has expired.'
            })
        
        # Check if merchant exists
        merchant = Merchant.objects.filter(merchantId=merchant_id).first()
        if not merchant:
            return render(request, 'entry_code.html', {
                'valid': False, 
                'error_message': 'Merchant not found.'
            })
        
        # Render the payment page
        return render(request, 'entry_code.html', {
            'valid': True,
            'merchant_id': merchant_id,
            'code_id': code_id,
            'merchant_name': merchant.merchantDisplayName or merchant.merchantName
        })


class EntryCodeConfirmView(APIView):
    """
    POST /entry-code/confirm
    Process the payment confirmation from entry code page
    """
    def buildPlaceOrderRequestDTO (self,request_dto:EntryCodeConfirmRequestDTO,user_agent)-> PlaceOrderRequestDTO:
        reference_order_id = str(uuid.uuid4())
        
        dto=PlaceOrderRequestDTO(
            order=OrderDTO(
                referenceOrderId=reference_order_id,
                orderDescription=f"Payment via Entry Code - {request_dto.merchantId}",
                orderAmount=AmountDTO(
                    currency=request_dto.currency,
                    value=request_dto.amount
                ),
                merchantId=request_dto.merchantId,
                env=EnvDTO(
                    userAgent=user_agent
                )
            ),
            paymentFactor=PaymentFactorDTO(
                isInStorePayment=True,
                isCashierPayment=True,
                inStorePaymentScenario="EntryCode"
            ),
            paymentAmount=AmountDTO(
                currency=request_dto.currency,
                value=request_dto.amount
            ),paymentMethod=PaymentMethodDTO(
                paymentMethodType="CONNECT_WALLET"
            )
        )
        return dto
    def process_place_order(self,request_dto: PlaceOrderRequestDTO) -> EntryCodeConfirmResponseDTO:


        # Generate payment request ID
        payment_request_id = str(uuid.uuid4())
        
        # Calculate expiry time (current time + 3 minutes in UTC+8 timezone)
        malaysia_tz = ZoneInfo("Asia/Kuala_Lumpur")
        expiry_time = datetime.now(malaysia_tz)
        
        # Get service instances
        signature_service, alipay_client, db_service = get_service_instances()
        isInStorePayment = request_dto.paymentFactor.isInStorePayment
        isCashierPayment = request_dto.paymentFactor.isCashierPayment
        
        try:
            if isInStorePayment:
                if isCashierPayment:
                    expiry_time = expiry_time + timedelta(minutes=3)
                else:
                    expiry_time = expiry_time + timedelta(minutes=1)
                
                # Build Alipay request DTO
                order = request_dto.order
                merchant_info = db_service.getMerchantInfo(merchant_id=order.merchantId)
                logger.debug(f"merchant info: {merchant_info}")
                if merchant_info:
                    alipay_request_dto = AlipayPayRequestDTO(
                        paymentRequestId=payment_request_id,
                        paymentAmount=AlipayAmountDTO(
                currency=request_dto.paymentAmount.currency,
                value=str(request_dto.paymentAmount.value)
            ),
                        paymentMethod=request_dto.paymentMethod,
                        paymentFactor=request_dto.paymentFactor,
                        paymentExpiryTime=expiry_time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
                        paymentRedirectUrl=f"https://superpayacqp-production.up.railway.app/payment-result?paymentRequestId={payment_request_id}",
                        paymentNotifyUrl="https://superpayacqp-production.up.railway.app/alipay/notifyPayment",
                        order=AlipayOrderDTO(
                            referenceOrderId=order.referenceOrderId if order.referenceOrderId else str(uuid.uuid4()),
                            orderDescription=order.orderDescription,
                            orderAmount=order.orderAmount,
                            merchant=MerchantInfoDTO(
                                referenceMerchantId=merchant_info.referenceMerchantId,
                                merchantName=merchant_info.merchantName,
                                merchantDisplayName=merchant_info.merchantDisplayName,
                                merchantMCC=merchant_info.merchantMCC,
                                merchantAddress=merchant_info.merchantAddress,
                                store=merchant_info.store,
                                currency=None
                            ),
                            goods=None,
                            shipping=order.shipping,
                            buyer=order.buyer,
                            env=order.env
                        ),
                        settlementStrategy=SettlementStrategyDTO(
                            settlementCurrency='MYR'
                        )
                    )
                    
                    # Call Alipay+ Pay API
                    alipay_response_dto = alipay_client.pay(alipay_request_dto)
                    
                    # Log API record
                    db_service.createApiRecordsWithReqRes(
                        '/aps/api/v1/payments/pay', 
                        HTTPMethod.POST, 
                        alipay_request_dto, 
                        alipay_response_dto, 
                        MessageType.OUTBOUND
                    )
                    
                    # Process result
                    result = alipay_response_dto.result
                    result_status = result.resultStatus
                    result_code = result.resultCode
                    
                    # Save payment request to database
                    db_service.savePaymentRequest(alipay_request_dto, alipay_response_dto, payment_request_id)
                    
                    # Handle UNKNOWN_EXCEPTION with retry
                    if result_status == 'U' and result_code == 'UNKNOWN_EXCEPTION':
                        alipay_response_dto = alipay_client.pay(alipay_request_dto)
                        db_service.createApiRecordsWithReqRes(
                        '/aps/api/v1/payments/pay', 
                        HTTPMethod.POST, 
                        alipay_request_dto, 
                        alipay_response_dto, 
                        MessageType.OUTBOUND
                    )
                    
                    # Map response
                    response_dto = EntryCodeConfirmResponseDTO(
                        result=alipay_response_dto.result,
                        paymentRequestId=payment_request_id,
                        paymentUrl=alipay_response_dto.paymentUrl
                    )
                else:
                    result = Result.returnMerchantNotRegistered()
                    response_dto = EntryCodeConfirmResponseDTO(result=result,paymentRequestId=payment_request_id)

            else:
                result = Result.returnProcessFail()
                response_dto = EntryCodeConfirmResponseDTO(result=result,paymentRequestId=payment_request_id)
            
            db_service.createApiRecordsWithReqRes(
                '/entry-code/confirm', 
                HTTPMethod.POST, 
                request_dto, 
                response_dto, 
                MessageType.INBOUND
            )
            
            return response_dto

        except Exception as e:
            logger.warning(f"Error in process_place_order: {e}")
            result = Result.returnProcessFail()
            response_dto = EntryCodeConfirmResponseDTO(result=result,paymentRequestId=payment_request_id)
            db_service.createApiRecordsWithReqRes(
                '/entry-code/confirm', 
                HTTPMethod.POST, 
                request_dto, 
                response_dto, 
                MessageType.INBOUND
            )
            return response_dto    
    def post(self, request):

        
        # Get request data

        try:
            request_dto = EntryCodeConfirmRequestDTO(**request.data)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            validated_response=self.entryCodeConfirmValidation(request_dto,user_agent)
            if validated_response != None:
                return validated_response
            
            request_body=self.buildPlaceOrderRequestDTO(request_dto,user_agent)
            response_dto = self.process_place_order(request_body)
            return Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK) 
        except Exception as e:
            return Response({
                'result': {
                    'resultCode': 'PROCESS_FAIL',
                    'resultStatus': 'F',
                    'resultMessage': str(e)
                }
            }, status=status.HTTP_200_OK)
    def entryCodeConfirmValidation (self,request_dto: EntryCodeConfirmRequestDTO,user_agent) -> Optional[Response] :
            
            is_valid_ua = any(identifier in user_agent for identifier in ALLOWED_UA_IDENTIFIERS)
        
            # if not is_valid_ua:
            #     logger.warning(f"Invalid User-Agent: {user_agent}")
            #     return Response({
            #     'result': {
            #         'resultCode': 'INVALID_USER_AGENT',
            #         'resultStatus': 'F',
            #         'resultMessage': 'Invalid User-Agent. Payment can only be initiated from authorized app.'
            #     }
            # }, status=status.HTTP_200_OK)
            entry_code = EntryCode.objects.filter(
            codeId=request_dto.codeId,
            merchantId=request_dto.merchantId,
            status='Active'
            ).first()
            if not entry_code:
                return Response({
                'result': {
                    'resultCode': 'INVALID_ENTRY_CODE',
                    'resultStatus': 'F',
                    'resultMessage': 'Invalid or expired entry code'
                }
            }, status=status.HTTP_200_OK)

            if entry_code.codeExpireTime < timezone.now():
                entry_code.status = 'Inactive'
                entry_code.save()
                return Response({
                'result': {
                    'resultCode': 'ENTRY_CODE_EXPIRED',
                    'resultStatus': 'F',
                    'resultMessage': 'Entry code has expired'
                }
            }, status=status.HTTP_200_OK)

            merchant = Merchant.objects.filter(merchantId=request_dto.merchantId).first()
            if not merchant:
                return Response({
                    'result': {
                        'resultCode': 'MERCHANT_NOT_FOUND',
                        'resultStatus': 'F',
                        'resultMessage': 'Merchant not found'
                    }
                }, status=status.HTTP_200_OK)

            return None
