"""
Alipay+ API Client
Handles communication with Alipay+ payment network
"""
import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Callable
import os
import requests
import uuid
from dtos.request import CancelPaymentRequestDTO, RefundRequestDTO, InquiryPaymentRequestDTO, AlipayPayRequestDTO
from dtos.response import (
    PaymentResponseDTO, 
    CancelPaymentResponseDTO, 
    RefundResponseDTO, 
    InquiryPaymentResponseDTO,
    AlipayPayResponseDTO
)

logger = logging.getLogger(__name__)


class RetryHandler:
    """
    Handles retry logic for API calls with configurable intervals
    """
    
    @staticmethod
    def retry_with_intervals(func: Callable, intervals: List[int], 
                            condition_check: Callable[[Any], bool]) -> Any:
        """
        Retry function with specified intervals until condition is met or retries exhausted
        
        Args:
            func: Function to call
            intervals: List of wait times in seconds between retries
            condition_check: Function that returns True if should stop retrying
        
        Returns:
            Last response from the function
        """
        response = func()
        
        if condition_check(response):
            return response
        
        for interval in intervals:
            time.sleep(interval)
            response = func()
            
            if condition_check(response):
                return response
        
        return response
    
    @staticmethod
    def retry_until_timeout(func: Callable, interval: int, timeout: int,
                           condition_check: Callable[[Any], bool]) -> Any:
        """
        Retry function at fixed interval until timeout
        
        Args:
            func: Function to call
            interval: Wait time in seconds between retries
            timeout: Total time in seconds to retry
            condition_check: Function that returns True if should stop retrying
        
        Returns:
            Last response from the function
        """
        start_time = time.time()
        response = func()
        
        if condition_check(response):
            return response
        
        while time.time() - start_time < timeout:
            time.sleep(interval)
            response = func()
            
            if condition_check(response):
                return response
        
        return response


class AlipayClient:
    """
    Client for interacting with Alipay+ API
    """
    
    BASE_URL = "https://open-sea.alipayplus.com"
    API_BASE_URL = os.getenv('API_BASE_URL')
    # API Endpoints
    PAY_ENDPOINT = "/aps/api/v1/payments/pay"
    CANCEL_ENDPOINT = "/aps/api/v1/payments/cancelPayment"
    REFUND_ENDPOINT = "/aps/api/v1/payments/refund"
    INQUIRY_ENDPOINT = "/aps/api/v1/payments/inquiryPayment"
    
    def __init__(self, signature_service, client_id: str):
        """
        Initialize Alipay+ client
        
        Args:
            signature_service: SignatureService instance
            client_id: Client identifier
        """
        self.signature_service = signature_service
        self.client_id = client_id
    
    def _get_request_time(self) -> str:
        """Get current UTC timestamp in ISO format"""
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    def _build_headers(self, request_uri: str, request_time: str, request_body: str) -> Dict[str, str]:
        """
        Build headers with signature
        
        Args:
            request_uri: Request URI path
            request_time: UTC timestamp
            request_body: Raw JSON request body
            
        Returns:
            Headers dictionary
        """
        signature = self.signature_service.generate_signature(
            "POST", request_uri, request_time, request_body
        )
        
        return {
            "Content-Type": "application/json; charset=UTF-8",
            "Client-Id": self.client_id,
            "Request-Time": request_time,
            "Signature": self.signature_service.build_signature_header(signature)
        }
    
    def _make_request(self, endpoint: str, payload: Dict[str, Any],timeout:int) -> Dict[str, Any]:
        """
        Make HTTP request to Alipay+ API
        
        Args:
            endpoint: API endpoint path
            payload: Request payload dictionary
            
        Returns:
            Response JSON dictionary
        """
        url = f"{self.BASE_URL}{endpoint}"
        request_time = self._get_request_time()
        request_body = json.dumps(payload, separators=(',', ':'))
        
        headers = self._build_headers(endpoint, request_time, request_body)
        
        # logger.info(f"Making request to Alipay+: {endpoint}")
        logger.debug(f"Request body: {request_body}")
        
        try:
            response = requests.post(url, headers=headers, data=request_body, timeout=timeout)
            response.raise_for_status()
            
# Verify response signature
            response_signature = response.headers.get('Signature')
            response_time = response.headers.get('Response-Time')
            
            # Only verify signature for successful responses (not errors)
            # Error responses from sandbox may not be signed
            response_json = response.json()

            if response_signature and response_time:
                sig_value = self.signature_service.extract_signature_from_header(response_signature)
                if sig_value:
                    is_valid = self.signature_service.verify_signature(
                        "POST", endpoint, response_time, response.text, sig_value
                    )
                    if not is_valid:
                        logger.warning("Response signature verification failed")

            
            logger.debug(f"Response: {response.text}")
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for {endpoint}")
            return {
                'result': {
                    'resultCode': 'TIMEOUT',
                    'resultStatus': 'U',
                    'resultMessage': 'Request timeout'
                }
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {endpoint}: {e}")
            return {
                'result': {
                    'resultCode': 'REQUEST_FAILED',
                    'resultStatus': 'F',
                    'resultMessage': str(e)
                }
            }
    
    def pay(self, request_dto: AlipayPayRequestDTO) -> AlipayPayResponseDTO:
        """
        Call Alipay+ Pay API
        
        Args:
            request_dto: AlipayPayRequestDTO instance
            
        Returns:
            PaymentResponseDTO instance
        """
        payload = request_dto.to_alipay_dict()
        response_data = self._make_request(self.PAY_ENDPOINT, payload,8)
        return AlipayPayResponseDTO(**response_data)
    
    def cancel_payment(self, request_dto: CancelPaymentRequestDTO) -> CancelPaymentResponseDTO:
        """
        Call Alipay+ cancelPayment API
        
        Args:
            request_dto: CancelPaymentRequestDTO instance
            
        Returns:
            CancelPaymentResponseDTO instance
        """
        payload = request_dto.model_dump(exclude_none=True)
        response_data = self._make_request(self.CANCEL_ENDPOINT, payload,8)
        return CancelPaymentResponseDTO(**response_data)
    
    def refund(self, request_dto: RefundRequestDTO) -> RefundResponseDTO:
        """
        Call Alipay+ Refund API
        
        Args:
            request_dto: RefundRequestDTO instance
            
        Returns:
            RefundResponseDTO instance
        """
        payload = request_dto.model_dump(exclude_none=True)
        response_data = self._make_request(self.REFUND_ENDPOINT, payload,8)
        return RefundResponseDTO(**response_data)
    
    def inquiry_payment(self, request_dto: InquiryPaymentRequestDTO) -> InquiryPaymentResponseDTO:
        """
        Call Alipay+ inquiryPayment API
        
        Args:
            request_dto: InquiryPaymentRequestDTO instance
            
        Returns:
            InquiryPaymentResponseDTO instance
        """
        payload = request_dto.model_dump(exclude_none=True)
        response_data = self._make_request(self.INQUIRY_ENDPOINT, payload,5)
        return InquiryPaymentResponseDTO(**response_data)



