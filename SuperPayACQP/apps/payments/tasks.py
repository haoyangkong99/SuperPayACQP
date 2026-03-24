"""
Background Tasks for Payment Processing
Handles PAYMENT_IN_PROCESS status with retry logic
"""
import logging
import time
from background_task import background

logger = logging.getLogger(__name__)


@background(schedule=5)  # Run 5 seconds after being called
def handle_payment_in_process_task(payment_request_id, max_retries=10):
    """
    Background task to handle PAYMENT_IN_PROCESS status.
    Periodically calls inquiryPayment until payment completes or max retries reached.
    
    Args:
        payment_request_id: The payment request ID to check
        max_retries: Maximum number of inquiry attempts (default: 10)
    """
    from django.conf import settings
    from dtos.request import InquiryPaymentRequestDTO
    from services.alipay_client import AlipayClient
    from services.signature_service import SignatureService
    from services.db_service import DbService
    from utils.constants import ResultStatus
    
    logger.info(f"Starting PAYMENT_IN_PROCESS handler for: {payment_request_id}")
    
    try:
        # Initialize services
        signature_service = SignatureService(
            private_key=settings.ALIPAY_PRIVATE_KEY,
            public_key=settings.ALIPAY_PUBLIC_KEY,
            client_id=settings.ALIPAY_CLIENT_ID
        )
        alipay_client = AlipayClient(signature_service, settings.ALIPAY_CLIENT_ID)
        db_service = DbService()
        
        # Retry intervals in seconds
        intervals = [2, 2, 3, 3, 5, 5, 10, 10, 10, 10]
        
        for i, interval in enumerate(intervals[:max_retries]):
            time.sleep(interval)
            
            try:
                # Call inquiryPayment
                inquiry_dto = InquiryPaymentRequestDTO(paymentRequestId=payment_request_id)
                response_dto = alipay_client.inquiry_payment(inquiry_dto)
                
                # Check the actual payment result, not the API call result
                payment_result = response_dto.paymentResult
                api_result = response_dto.result
                
                logger.debug(f"Inquiry attempt {i+1} for {payment_request_id}: payment_status={payment_result.resultStatus if payment_result else 'N/A'}, payment_code={payment_result.resultCode if payment_result else 'N/A'}, api_status={api_result.resultStatus}")
                
                # Update database with latest info
                db_service.updatePaymentRequestResultByInquiryPayment(response_dto)
                
                # Check if payment is complete using paymentResult (actual payment status)
                if payment_result:
                    if payment_result.resultStatus == ResultStatus.SUCCESS.value:
                        logger.info(f"Payment completed successfully: {payment_request_id}")
                        return
                    
                    if payment_result.resultStatus == ResultStatus.FAILURE.value:
                        logger.info(f"Payment failed: {payment_request_id}")
                        return
                
                # Continue retrying for UNKNOWN status (PAYMENT_IN_PROCESS, UNKNOWN_EXCEPTION, etc.)
                
            except Exception as e:
                logger.error(f"Error in inquiry attempt {i+1} for {payment_request_id}: {e}")
                # Continue to next retry
        
        logger.warning(f"Max retries ({max_retries}) reached for payment: {payment_request_id}")
        
    except Exception as e:
        logger.error(f"Fatal error in PAYMENT_IN_PROCESS handler for {payment_request_id}: {e}")
