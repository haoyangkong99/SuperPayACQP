import json
import logging
import uuid
import os
from datetime import datetime, timedelta, timezone as dt_timezone
from typing import Optional

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
)
from dtos.response import (
    PaymentResponseDTO, 
    CancelPaymentResponseDTO, 
    InquiryPaymentResponseDTO,
    NotifyPaymentResponseDTO,
    BaseResponseDTO
)
from django.utils import timezone

from utils.constants import Result,MessageType,HTTPMethod,ALLOWED_UA_IDENTIFIERS
from services.alipay_client import AlipayClient, RetryHandler
from services.signature_service import SignatureService
from services.db_service import DbService

logger = logging.getLogger(__name__)


def get_service_instances():
    """Get signature service and Alipay client instances"""

    db_service=DbService()
    return db_service


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
            dbService=get_service_instances()
            dbService.createMerchants(request_dto)
            result = Result.returnSuccess()
            response=BaseResponseDTO(
                    result=result
                )
            dbService.createApiRecordsWithReqRes('api/merchants',HTTPMethod.POST,request_dto,response,MessageType.INBOUND)
            return Response(response.model_dump(exclude_none=True), status=status.HTTP_200_OK)
        except Exception as e:
            logger.warning(f"error: {e}")
            result = Result.returnProcessFail()
            response=BaseResponseDTO(
                    result=result
                )
            return Response(response.model_dump(exclude_none=True), status=status.HTTP_200_OK)


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
            entry_code_url = f"{base_url}/entry-code?merchantId={merchant_id}&codeId={code_id}"
            
            result = Result.returnSuccess()
            response = {
                'result': result.model_dump(),
                'entryCodeUrl': entry_code_url
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
    
    def post(self, request):

        
        # Get request data
        merchant_id = request.data.get('merchantId')
        code_id = request.data.get('codeId')
        currency = request.data.get('currency')
        amount = request.data.get('amount')
        
        # Validate required fields
        if not all([merchant_id, code_id, currency, amount]):
            return Response({
                'result': {
                    'resultCode': 'INVALID_REQUEST',
                    'resultStatus': 'F',
                    'resultMessage': 'Missing required fields'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get User-Agent from request header
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        logger.debug(f"User-Agent: {user_agent}")
        
        # Validate User-Agent - check if it contains AlipayClient or AlipayConnect
        is_valid_ua = any(identifier in user_agent for identifier in ALLOWED_UA_IDENTIFIERS)
        
        if not is_valid_ua:
            logger.warning(f"Invalid User-Agent: {user_agent}")
            return Response({
                'result': {
                    'resultCode': 'INVALID_USER_AGENT',
                    'resultStatus': 'F',
                    'resultMessage': 'Invalid User-Agent. Payment can only be initiated from authorized app.'
                }
            }, status=status.HTTP_200_OK)
        
        # Validate entry code
        entry_code = EntryCode.objects.filter(
            codeId=code_id,
            merchantId=merchant_id,
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
        
        # Check if entry code is expired
        
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
        
        try:
            # Convert amount to smallest unit (e.g., MYR 1.00 = 100)
            amount_in_smallest_unit = int(float(amount) * 100)
            
            # Get merchant info
            merchant = Merchant.objects.filter(merchantId=merchant_id).first()
            if not merchant:
                return Response({
                    'result': {
                        'resultCode': 'MERCHANT_NOT_FOUND',
                        'resultStatus': 'F',
                        'resultMessage': 'Merchant not found'
                    }
                }, status=status.HTTP_200_OK)
            
            # Build place order request
            base_url = os.getenv('API_BASE_URL')
            place_order_url = f"{base_url}/api/place-order"
            
            # Generate reference order ID
            reference_order_id = str(uuid.uuid4())
            
            # Build request body
            request_body = {
                "paymentFactor": {
                    "isInStorePayment": True,
                    "isCashierPayment": True,
                    "inStorePaymentScenario": "EntryCode"
                },
                "order": {
                    "referenceOrderId": reference_order_id,
                    "orderDescription": f"Payment via Entry Code - {merchant.merchantDisplayName or merchant.merchantName}",
                    "orderAmount": {
                        "currency": currency,
                        "value": amount_in_smallest_unit
                    },
                    "merchantId": merchant_id,
                    "env": {
                        "userAgent": user_agent
                    }
                },
                "paymentAmount": {
                    "currency": currency,
                    "value": amount_in_smallest_unit
                },
                "paymentMethod": {
                    "paymentMethodType": "CONNECT_WALLET"
                }
            }
            
            # Call place order API
            headers = {
                'Content-Type': 'application/json',
                'Merchant-ID': merchant_id
            }
            
            logger.debug(f"Calling place order API: {place_order_url}")
            logger.debug(f"Request body: {request_body}")
            
            response = http_requests.post(place_order_url, json=request_body, headers=headers, timeout=30)
            response_data = response.json()
            
            logger.debug(f"Place order response: {response_data}")
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error processing entry code payment: {e}")
            return Response({
                'result': {
                    'resultCode': 'PROCESS_FAIL',
                    'resultStatus': 'F',
                    'resultMessage': str(e)
                }
            }, status=status.HTTP_200_OK)
