import json
import logging
import uuid
import random
import string
from datetime import datetime, timedelta, timezone
from typing import Optional
from utils.helpers import format_str_to_datetime
from django.conf import settings
from django.db import transaction
from apps.api_records.api_records_models import ApiRecord
from apps.orders.orders_models import Order, OrderGoods
from apps.payments.payments_models import PaymentRequest,Settlement
from apps.merchants.merchants_models import Merchant
from apps.refunds.refund_models import RefundRecord
from utils.constants import Result,ResultStatus,PaymentStatus
from dtos.response import PaymentResponseDTO
from dtos.request import (
    PlaceOrderRequestDTO, 
    CancelPaymentRequestDTO, 
    InquiryPaymentRequestDTO,
    StoreDTO,
    AddressDTO,
    NotifyPaymentRequestDTO
)
from dtos.request import (
    AlipayPayRequestDTO, 
    PaymentMethodDTO, 
    AlipayOrderDTO,
    MerchantInfoDTO,
    RefundRequestDTO,
    AmountDTO,
    PrivatePlaceOrderRequestDTO,
    SettlementStrategyDTO
)
from dtos.response import (
    PaymentResponseDTO, 
    CancelPaymentResponseDTO, 
    InquiryPaymentResponseDTO,
    NotifyPaymentResponseDTO,
    AlipayPayResponseDTO,
    RefundResponseDTO,
    PrivatePlaceOrderResponseDTO,
    SettlementQuoteDTO
)
from zoneinfo import ZoneInfo
from dtos.request import RefundRequestDTO
logger = logging.getLogger(__name__)


def generate_merchant_id(prefix: str = "MC", max_length: int = 32) -> str:
    """
    Generate a random merchant ID with a maximum length of 32 characters.
    
    Format: {prefix}{timestamp_suffix}{random_chars}
    - prefix: Default "MC" (2 characters)
    - timestamp_suffix: Last 6 digits of current timestamp (6 characters)
    - random_chars: Random alphanumeric characters to fill remaining space
    
    Args:
        prefix: Prefix for the merchant ID (default: "MC")
        max_length: Maximum length of the merchant ID (default: 32)
    
    Returns:
        A unique merchant ID string with maximum length of 32 characters
    
    Example:
        generate_merchant_id() -> "MC250326ABC123XYZ" (varies)
        generate_merchant_id(prefix="STORE") -> "STORE250326ABC123" (varies)
    """
    # Calculate remaining length after prefix
    remaining_length = max_length - len(prefix)
    
    if remaining_length <= 0:
        raise ValueError(f"Prefix '{prefix}' exceeds maximum length of {max_length}")
    
    # Use last 6 digits of timestamp for uniqueness
    timestamp_suffix = str(int(datetime.now(timezone.utc).timestamp()))[-6:]
    
    # Calculate space for random characters
    random_length = remaining_length - len(timestamp_suffix)
    
    if random_length < 0:
        # If timestamp doesn't fit, truncate it
        timestamp_suffix = timestamp_suffix[:remaining_length]
        random_length = 0
    
    # Generate random alphanumeric characters (uppercase for readability)
    random_chars = ''.join(
        random.choices(string.ascii_uppercase + string.digits, k=random_length)
    ) if random_length > 0 else ''
    
    # Combine parts
    merchant_id = f"{prefix}{timestamp_suffix}{random_chars}"
    
    # Ensure we don't exceed max_length
    return merchant_id[:max_length]


class DbService:

    @staticmethod
    @transaction.atomic
    def createApiRecordsWithReqRes(api_url, http_method, request, response, message_type):
        # Handle both dict and Pydantic model objects
        if isinstance(request, dict):
            request_body = json.dumps(request)
        elif isinstance(request,str):
            request_body=request
        else:
            request_body = request.model_dump_json(exclude_none=True)
        
        if isinstance(response, dict):
            response_body = json.dumps(response)
        elif isinstance(response,str):
            response_body=response
        else:
            response_body = response.model_dump_json()
        
        ApiRecord.objects.create(
            api_url=api_url,
            http_method=http_method,
            request_body=request_body,
            response_body=response_body,
            message_type=message_type
        )

    @staticmethod
    @transaction.atomic
    def createApiRecordsWithReq(api_url, http_method, request, message_type):
        # Handle both dict and Pydantic model objects
        if isinstance(request, dict):
            request_body = json.dumps(request)
        else:
            request_body = request.model_dump_json(exclude_none=True)
        
        ApiRecord.objects.create(
            api_url=api_url,
            http_method=http_method,
            request_body=request_body,
            message_type=message_type
        )

    @staticmethod
    @transaction.atomic
    def savePaymentRequest(request_dto: AlipayPayRequestDTO,
                           response_dto: AlipayPayResponseDTO,
                           payment_request_id: str):
            status=""
            match response_dto.result.resultStatus:
                case ResultStatus.SUCCESS:
                      status=PaymentStatus.SUCCESS.value
                case ResultStatus.FAILURE:
                      status=PaymentStatus.FAILED.value
                case ResultStatus.UNKNOWN:
                      status=PaymentStatus.PENDING.value
            value=None
            if isinstance (request_dto.paymentAmount.value,str):
                value=int (request_dto.paymentAmount.value)
            else:
                value=request_dto.paymentAmount.value

            PaymentRequest.objects.update_or_create(
                paymentRequestId=payment_request_id,
                defaults={
                    'acquirerId': response_dto.acquirerId or '',
                    'paymentAmountValue': value,
                    'paymentAmountCurrency': request_dto.paymentAmount.currency,
                    'paymentMethodType': request_dto.paymentMethod.paymentMethodType,
                    'paymentMethodId': request_dto.paymentMethod.paymentMethodId,
                    'customerId': request_dto.paymentMethod.customerId,
                    'paymentMethodMetaData': request_dto.paymentMethod.paymentMethodMetaData,
                    'isInStorePayment': request_dto.paymentFactor.isInStorePayment,
                    'isCashierPayment': request_dto.paymentFactor.isCashierPayment,
                    'inStorePaymentScenario': request_dto.paymentFactor.inStorePaymentScenario,
                    'paymentExpiryTime': request_dto.paymentExpiryTime,
                    'paymentNotifyUrl': request_dto.paymentNotifyUrl,
                    'paymentRedirectUrl': request_dto.paymentRedirectUrl,
                    'splitSettlementId': request_dto.splitSettlementId,
                    'settlementStrategy': request_dto.settlementStrategy.model_dump(exclude_none=True) if request_dto.settlementStrategy else None,
                    'paymentId': response_dto.paymentId or None,
                    'paymentTime': response_dto.paymentTime,
                    'pspId': response_dto.pspId or None,
                    'walletBrandName': response_dto.walletBrandName or None,
                    'mppPaymentId': response_dto.mppPaymentId or None,
                    'customsDeclarationAmountValue': response_dto.customsDeclarationAmount.value if response_dto.customsDeclarationAmount else None,
                    'customsDeclarationAmountCurrency': response_dto.customsDeclarationAmount.currency if response_dto.customsDeclarationAmount else None,
                    'resultStatus': response_dto.result.resultStatus,
                    'resultCode': response_dto.result.resultCode,
                    'resultMessage': response_dto.result.resultMessage,
                    'paymentStatus': status
                }
            )
            
            order = request_dto.order
            if order:
                orderId = str(uuid.uuid4())
                
                # Create Order with null checks
                Order.objects.update_or_create(
                    paymentRequestId=request_dto.paymentRequestId,
                    defaults={
                        'paymentRequestId':request_dto.paymentRequestId,
                        'orderId':orderId,
                        'referenceOrderId': order.referenceOrderId,
                        'orderDescription': order.orderDescription,
                        'orderAmountValue': order.orderAmount.value,
                        'orderAmountCurrency': order.orderAmount.currency,
                        'merchantId': order.merchant.referenceMerchantId if order.merchant else '',
                        'shippingName': order.shipping.shippingName.model_dump(exclude_none=True) if order.shipping and order.shipping.shippingName else None,
                        'shippingPhoneNo': order.shipping.shippingPhoneNo if order.shipping else '',
                        'shippingAddress': order.shipping.shippingAddress.model_dump(exclude_none=True) if order.shipping and order.shipping.shippingAddress else None,
                        'shippingCarrier': order.shipping.shippingCarrier if order.shipping else '',
                        'referenceBuyerId': order.buyer.referenceBuyerId if order.buyer else '',
                        'buyerName': order.buyer.buyerName.model_dump(exclude_none=True) if order.buyer and order.buyer.buyerName else None,
                        'buyerPhoneNo': order.buyer.buyerPhoneNo if order.buyer else '',
                        'buyerEmail': order.buyer.buyerEmail if order.buyer else '',
                        'env': order.env.model_dump(exclude_none=True) if order.env else None,
                        'indirectAcquirer': order.indirectAcquirer.model_dump(exclude_none=True) if order.indirectAcquirer else None
                    }
                )
                
                # Create OrderGoods for each item
                if order.goods:
                    for g in order.goods:
                        OrderGoods.objects.update_or_create(
                            orderId=orderId,
                            referenceGoodsId=g.referenceGoodsId or '',
                            defaults={
                                'goodsName': g.goodsName or '',
                                'goodsCategory': g.goodsCategory or '',
                                'goodsBrand': g.goodsBrand or '',
                                'goodsUnitAmountValue': g.goodsUnitAmount.value if g.goodsUnitAmount else None,
                                'goodsUnitAmountCurrency': g.goodsUnitAmount.currency if g.goodsUnitAmount else None,
                                'goodsQuantity': g.goodsQuantity
                            }
                        )
            
            if response_dto.settlementAmount:
                # Check if settlement already exists for this paymentRequestId
                existing_settlement = Settlement.objects.filter(paymentRequestId=request_dto.paymentRequestId).first()
                
                # Helper to convert datetime string to datetime object
                def parse_datetime_str(dt_str):
                    if dt_str is None:
                        return None
                    try:
                        return format_str_to_datetime(dt_str)
                    except Exception:
                        return None
                
                # Helper to convert price to Decimal
                def to_decimal(value):
                    from decimal import Decimal
                    if value is None:
                        return None
                    return Decimal(str(value))
                
                if existing_settlement:
                    existing_settlement.settlementAmountValue = response_dto.settlementAmount.value
                    existing_settlement.settlementCurrency = response_dto.settlementAmount.currency or 'MYR'
                    if response_dto.settlementQuote:
                        existing_settlement.quoteId = response_dto.settlementQuote.quoteId
                        existing_settlement.quotePrice = to_decimal(response_dto.settlementQuote.quotePrice)
                        existing_settlement.quoteCurrencyPair = response_dto.settlementQuote.quoteCurrencyPair
                        existing_settlement.quoteStartTime = parse_datetime_str(response_dto.settlementQuote.quoteStartTime)
                        existing_settlement.quoteExpiryTime = parse_datetime_str(response_dto.settlementQuote.quoteExpiryTime)
                        existing_settlement.quoteUnit = response_dto.settlementQuote.quoteUnit
                        existing_settlement.baseCurrency = response_dto.settlementQuote.baseCurrency
                    existing_settlement.save()
                else:
                    Settlement.objects.create(
                        settlementId=str(uuid.uuid4()),
                        paymentRequestId=request_dto.paymentRequestId,
                        settlementAmountValue=response_dto.settlementAmount.value,
                        settlementCurrency=response_dto.settlementAmount.currency,
                        quoteId=response_dto.settlementQuote.quoteId if response_dto.settlementQuote else None,
                        quotePrice=to_decimal(response_dto.settlementQuote.quotePrice) if response_dto.settlementQuote else None,
                        quoteCurrencyPair=response_dto.settlementQuote.quoteCurrencyPair if response_dto.settlementQuote else None,
                        quoteStartTime=parse_datetime_str(response_dto.settlementQuote.quoteStartTime) if response_dto.settlementQuote else None,
                        quoteExpiryTime=parse_datetime_str(response_dto.settlementQuote.quoteExpiryTime) if response_dto.settlementQuote else None,
                        quoteUnit=response_dto.settlementQuote.quoteUnit if response_dto.settlementQuote else None,
                        baseCurrency=response_dto.settlementQuote.baseCurrency if response_dto.settlementQuote else None,
                    )
                        

    @staticmethod
    @transaction.atomic
    def updatePaymentRequestResult (payment_request_id:str,result:Result):

            paymentRequest=PaymentRequest.objects.filter(paymentRequestId=payment_request_id).first()
            if paymentRequest:
                paymentRequest.resultStatus=result.resultStatus.value
                paymentRequest.resultCode=result.resultCode if result.resultCode is not None else ''
                paymentRequest.resultMessage=result.resultMessage if result.resultMessage is not None else ''
                paymentRequest.save()
            
 
    @staticmethod
    @transaction.atomic
    def updatePaymentRequestResultByNotifyPayment (notification_dto: NotifyPaymentRequestDTO,payment_request_id:str):
                payment_request = PaymentRequest.objects.get(paymentRequestId=notification_dto.paymentRequestId)
                if (payment_request.resultStatus=='U' and payment_request.paymentStatus==PaymentStatus.PENDING):
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
                    if notification_dto.acquirerId:
                        payment_request.acquirerId=notification_dto.acquirerId
                    if notification_dto.customerId:
                        payment_request.customerId=notification_dto.customerId
                    if notification_dto.mppPaymentId:
                        payment_request.mppPaymentId=notification_dto.mppPaymentId
                    
                    payment_request.resultStatus=notification_dto.paymentResult.resultStatus
                    payment_request.resultCode=notification_dto.paymentResult.resultCode
                    payment_request.resultMessage=notification_dto.paymentResult.resultMessage
                    if notification_dto.paymentResult.resultStatus=='S':
                        payment_request.paymentStatus=PaymentStatus.SUCCESS
                    else:
                        payment_request.paymentStatus=PaymentStatus.FAILED                    
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
                                settlementCurrency=settlement_amount.currency, 
                                quoteId=settlement_quote.quoteId if settlement_quote else None,
                                quotePrice=settlement_quote.quotePrice if settlement_quote else None,
                                quoteCurrencyPair=settlement_quote.quoteCurrencyPair if settlement_quote else None,
                                quoteStartTime=settlement_quote.quoteStartTime if settlement_quote else None,
                                quoteExpiryTime=settlement_quote.quoteExpiryTime if settlement_quote else None,
                                quoteUnit=settlement_quote.quoteUnit if settlement_quote else None,
                                baseCurrency=settlement_quote.baseCurrency if settlement_quote else None
                            )

    @staticmethod
    @transaction.atomic
    def updatePaymentRequestResultByCancelled (payment_request_id:str,result:Result):

            paymentRequest=PaymentRequest.objects.filter(paymentRequestId=payment_request_id).first()
            if paymentRequest:
                paymentRequest.resultStatus=ResultStatus.FAILURE
                paymentRequest.resultCode='ORDER_IS_CLOSED'
                paymentRequest.resultMessage="order is closed"
                paymentRequest.paymentStatus=PaymentStatus.CANCELLED.value
                paymentRequest.save()

    @staticmethod
    @transaction.atomic
    def updatePaymentRequestResultByInquiryPayment(request_dto:InquiryPaymentRequestDTO,response_dto: InquiryPaymentResponseDTO) -> bool:

        payment_request_id = response_dto.paymentRequestId or request_dto.paymentRequestId
        if not payment_request_id:
            logger.warning("Cannot update PaymentRequest: paymentRequestId is missing from response")
            return False
        
        payment_request = PaymentRequest.objects.filter(paymentRequestId=payment_request_id).first()
        if not payment_request:
            logger.warning(f"PaymentRequest not found: {payment_request_id}")
            return False
        
        # Track if any fields were updated
        updated = False
        
        # Helper function to compare and update a field
        def update_if_different(field_name: str, new_value, old_value):
            nonlocal updated
            # Handle None vs empty string comparison
            old_normalized = old_value if old_value is not None else None
            new_normalized = new_value if new_value is not None else None
            
            if new_normalized != old_normalized:
                setattr(payment_request, field_name, new_value)
                logger.debug(f"Updated {field_name}: '{old_value}' -> '{new_value}'")
                updated = True
                return True
            return False
        
        # Update paymentId
        if response_dto.paymentId:
            update_if_different('paymentId', response_dto.paymentId, payment_request.paymentId)
        
        # Update acquirerId
        if response_dto.acquirerId:
            update_if_different('acquirerId', response_dto.acquirerId, payment_request.acquirerId)
        
        # Update pspId
        if response_dto.pspId:
            update_if_different('pspId', response_dto.pspId, payment_request.pspId)
        
        # Update customerId
        if response_dto.customerId:
            update_if_different('customerId', response_dto.customerId, payment_request.customerId)
        
        # Update walletBrandName
        if response_dto.walletBrandName:
            update_if_different('walletBrandName', response_dto.walletBrandName, payment_request.walletBrandName)
        
        # Update mppPaymentId
        if response_dto.mppPaymentId:
            update_if_different('mppPaymentId', response_dto.mppPaymentId, payment_request.mppPaymentId)
        
        # Update paymentTime (convert string to datetime)
        if response_dto.paymentTime:
            
            try:
                payment_time = format_str_to_datetime(response_dto.paymentTime)
                old_payment_time = payment_request.paymentTime
                if payment_time != old_payment_time:
                    payment_request.paymentTime = payment_time
                    logger.debug(f"Updated paymentTime: '{old_payment_time}' -> '{payment_time}'")
                    updated = True
            except Exception as e:
                logger.warning(f"Failed to parse paymentTime: {response_dto.paymentTime}, error: {e}")
        if payment_request.resultStatus=='U' and response_dto.paymentResult:
            payment_request.resultStatus=response_dto.paymentResult.resultStatus
            payment_request.resultCode=response_dto.paymentResult.resultCode
            payment_request.resultMessage=response_dto.paymentResult.resultMessage
            if response_dto.paymentResult.resultStatus=='S':
                payment_request.paymentStatus=PaymentStatus.SUCCESS
            if response_dto.paymentResult.resultStatus=='F':
                payment_request.paymentStatus=PaymentStatus.FAILED
            updated=True
        
        # Update settlement if present
        if response_dto.settlementAmount:
            # settlementQuote is SettlementQuoteDTO (Pydantic model)
            settlement_quote = response_dto.settlementQuote
            
            # Helper to convert datetime string to datetime object
            def parse_datetime_str(dt_str):
                if dt_str is None:
                    return None
                try:
                    return format_str_to_datetime(dt_str)
                except Exception:
                    return None
            
            # Helper to convert price to Decimal
            def to_decimal(value):
                from decimal import Decimal
                if value is None:
                    return None
                return Decimal(str(value))
            
            if settlement_quote:
                quote_id = settlement_quote.quoteId
                quote_price = to_decimal(settlement_quote.quotePrice)
                quote_currency_pair = settlement_quote.quoteCurrencyPair
                quote_start_time = parse_datetime_str(settlement_quote.quoteStartTime)
                quote_expiry_time = parse_datetime_str(settlement_quote.quoteExpiryTime)
                quote_unit = settlement_quote.quoteUnit
                base_currency = settlement_quote.baseCurrency
            else:
                quote_id = None
                quote_price = None
                quote_currency_pair = None
                quote_start_time = None
                quote_expiry_time = None
                quote_unit = None
                base_currency = None
            
            # Check if settlement already exists for this paymentRequestId
            existing_settlement = Settlement.objects.filter(paymentRequestId=payment_request_id).first()
            
            if existing_settlement:
                # Update existing settlement
                existing_settlement.settlementAmountValue = response_dto.settlementAmount.value
                existing_settlement.settlementCurrency = response_dto.settlementAmount.currency or 'MYR'
                existing_settlement.quotePrice = quote_price
                existing_settlement.quoteCurrencyPair = quote_currency_pair
                existing_settlement.quoteStartTime = quote_start_time
                existing_settlement.quoteExpiryTime = quote_expiry_time
                existing_settlement.quoteUnit = quote_unit
                existing_settlement.baseCurrency = base_currency
                existing_settlement.save()
                logger.debug(f"Updated settlement for paymentRequestId: {payment_request_id}")
            else:
                # Create new settlement with generated settlementId
                Settlement.objects.create(
                    settlementId=str(uuid.uuid4()),
                    paymentRequestId=payment_request_id,
                    settlementAmountValue=response_dto.settlementAmount.value,
                    settlementCurrency=response_dto.settlementAmount.currency or 'MYR',
                    quoteId=quote_id,
                    quotePrice=quote_price,
                    quoteCurrencyPair=quote_currency_pair,
                    quoteStartTime=quote_start_time,
                    quoteExpiryTime=quote_expiry_time,
                    quoteUnit=quote_unit,
                    baseCurrency=base_currency,
                )
                logger.debug(f"Created new settlement for paymentRequestId: {payment_request_id}")
                updated = True
        
        # Save if any fields were updated
        if updated:
            payment_request.save()
            logger.info(f"PaymentRequest {payment_request_id} updated with {len([f for f in [payment_request.paymentId, payment_request.pspId, payment_request.customerId, payment_request.walletBrandName, payment_request.mppPaymentId, payment_request.paymentTime, payment_request.resultStatus, payment_request.paymentStatus]])} field changes")
        else:
            logger.debug(f"No changes detected for PaymentRequest {payment_request_id}")
        
        return updated
            
    @staticmethod
    def getMerchantInfo(merchant_id: str) -> Optional[MerchantInfoDTO]:
        """Get merchant info from database"""
        

        merchant = Merchant.objects.filter(merchantId=merchant_id).first()
        if merchant:
            # Build store info (required by Alipay+)
            store = None
            if merchant.store and isinstance(merchant.store, dict):
                tempStore = StoreDTO(**merchant.store)
                store=StoreDTO(
                     referenceStoreId=tempStore.referenceStoreId,
                     storeName=tempStore.storeName,
                     storeMCC=tempStore.storeMCC
                )
            
            
            # Truncate state to 8 characters (Alipay+ limit)
            merchant_address = merchant.merchantAddress or {}
            if merchant_address and 'state' in merchant_address and len(str(merchant_address.get('state', ''))) > 8:
                merchant_address = {**merchant_address, 'state': str(merchant_address['state'])[:8]}
            
            # Convert dict to AddressDTO
            address_dto = AddressDTO(**merchant_address) 
  
            return MerchantInfoDTO(
                referenceMerchantId=merchant.merchantId,
                merchantName=merchant.merchantName ,
                merchantDisplayName=merchant.merchantDisplayName ,
                merchantMCC=merchant.merchantMCC,
                merchantAddress=address_dto,
                store=store,
                currency=merchant.currency
            )
        else:
             return None

    @staticmethod
    @transaction.atomic
    def createMerchants(request: MerchantInfoDTO):
        merchant=Merchant.objects.filter(merchantId=request.referenceMerchantId).first()
        if merchant:
            merchant.merchantName = request.merchantName 
            merchant.merchantDisplayName=request.merchantDisplayName 
            merchant.merchantMCC=request.merchantMCC 
            merchant.merchantAddress=request.merchantAddress.model_dump(exclude_none=True)   # type: ignore[assignment]
            merchant.store=request.store.model_dump(exclude_none=True) if request.store else None  # type: ignore[assignment]
            merchant.currency=request.currency or 'MYR'
            merchant.save()

        else:
            Merchant.objects.create(
            merchantId=request.referenceMerchantId if request.referenceMerchantId else generate_merchant_id(),
            merchantName=request.merchantName,
            merchantDisplayName=request.merchantDisplayName,
            merchantRegisterDate= request.merchantRegisterDate if request.merchantRegisterDate else str(datetime.now(timezone.utc)),
            merchantMCC=request.merchantMCC,
            merchantAddress=request.merchantAddress.model_dump(exclude_none=True) ,
            store=request.store.model_dump(exclude_none=True) if request.store else None,
            currency=request.currency
        )
    
    @staticmethod
    @transaction.atomic
    def createRefundRecord (request_dto:RefundRequestDTO, response_dto: RefundResponseDTO):
        paymentRequestId=request_dto.paymentRequestId
        paymentId=request_dto.paymentId
        if not request_dto.paymentRequestId and request_dto.paymentId:
            paymentRequestId=PaymentRequest.objects.get(paymentId=request_dto.paymentId).paymentRequestId
        if not request_dto.paymentId and request_dto.paymentRequestId:
            paymentId=PaymentRequest.objects.get(paymentRequestId=request_dto.paymentRequestId).paymentId

        refund_record=RefundRecord.objects.filter(refundRequestId=request_dto.refundRequestId).first()
        if (refund_record):
            refund_record.resultStatus=response_dto.result.resultStatus
            refund_record.resultCode=response_dto.result.resultCode
            refund_record.resultMessage=response_dto.result.resultMessage
            refund_record.save()
        else:
             RefundRecord.objects.create(
                    refundRequestId=request_dto.refundRequestId,
                    paymentRequestId=paymentRequestId,
                    paymentId=paymentId,
                    refundAmountValue=request_dto.refundAmount.value,
                    refundAmountCurrency=request_dto.refundAmount.currency,
                    refundReason=request_dto.refundReason or None,
                    resultStatus=response_dto.result.resultStatus,
                    resultCode=response_dto.result.resultCode,
                    resultMessage=response_dto.result.resultMessage
                )
    @staticmethod
    def buildInquiryPaymentResponseFromDB(payment_request: PaymentRequest) -> InquiryPaymentResponseDTO:

        if payment_request.resultStatus=='F':
            return InquiryPaymentResponseDTO(
                result=Result.returnSuccess(),
                paymentResult=Result(resultStatus=ResultStatus.FAILURE,resultCode=payment_request.resultCode or '',resultMessage=payment_request.resultMessage or '')
            )
        else:
            # Build payment amount
            payment_amount = None
            if payment_request.paymentAmountValue and payment_request.paymentAmountCurrency:
                payment_amount = AmountDTO(
                    currency=payment_request.paymentAmountCurrency,
                    value=payment_request.paymentAmountValue
                )
            
            # Build customs declaration amount
            customs_declaration_amount = None
            if payment_request.customsDeclarationAmountValue and payment_request.customsDeclarationAmountCurrency:
                customs_declaration_amount = AmountDTO(
                    currency=payment_request.customsDeclarationAmountCurrency,
                    value=payment_request.customsDeclarationAmountValue
                )
            
            # Build settlement amount and quote from Settlement model
            settlement_amount = None
            settlement_quote = None
            settlement = Settlement.objects.filter(paymentRequestId=payment_request.paymentRequestId).first()
            if settlement:
                settlement_amount = AmountDTO(
                    currency=settlement.settlementCurrency,
                    value=settlement.settlementAmountValue
                )
                if settlement.quoteId:
                    settlement_quote = SettlementQuoteDTO(
                        quoteId=settlement.quoteId,
                        quoteCurrencyPair=settlement.quoteCurrencyPair,
                        quotePrice=float(settlement.quotePrice) if settlement.quotePrice else None,
                        quoteStartTime=settlement.quoteStartTime.isoformat() if settlement.quoteStartTime else None,
                        quoteExpiryTime=settlement.quoteExpiryTime.isoformat() if settlement.quoteExpiryTime else None,
                        quoteUnit=settlement.quoteUnit,
                        baseCurrency=settlement.baseCurrency
                    )

            # Build payment result
            payment_result = Result(
                        resultStatus=ResultStatus.SUCCESS ,
                        resultCode=payment_request.resultCode or '',
                        resultMessage=payment_request.resultMessage or ''
                    )
                
            
            # Format payment time
            payment_time = None
            if payment_request.paymentTime:
                payment_time = payment_request.paymentTime.strftime("%Y-%m-%dT%H:%M:%S+08:00")
            
            return InquiryPaymentResponseDTO(
                result=Result.returnSuccess(),
                paymentResult=payment_result,
                acquirerId=payment_request.acquirerId,
                pspId=payment_request.pspId,
                paymentRequestId=payment_request.paymentRequestId,
                paymentId=payment_request.paymentId,
                paymentAmount=payment_amount,
                paymentTime=payment_time ,
                customerId=payment_request.customerId,
                walletBrandName=payment_request.walletBrandName,
                settlementAmount=settlement_amount,
                settlementQuote=settlement_quote,
                customsDeclarationAmount=customs_declaration_amount,
                mppPaymentId=payment_request.mppPaymentId,
                transactions=None
            )

    @staticmethod
    @transaction.atomic
    def savePrivatePlaceOrder(request_dto: PrivatePlaceOrderRequestDTO) -> PaymentRequest:
            malaysia_tz = ZoneInfo("Asia/Kuala_Lumpur")
            expiry_time=datetime.now(malaysia_tz)+timedelta(minutes=3)
            payment_request_id=str(uuid.uuid4())
            payment_request=PaymentRequest.objects.create(
                paymentRequestId=payment_request_id,
                paymentAmountValue=request_dto.paymentAmount.value,
                paymentAmountCurrency=request_dto.paymentAmount.currency,
                paymentMethodType="CONNECT_WALLET",
                isInStorePayment=True,
                isCashierPayment=True,
                inStorePaymentScenario="OrderCode",
                paymentExpiryTime=expiry_time,
                paymentNotifyUrl="https://superpayacqp.onrender.com/alipay/notifyPayment",
                paymentRedirectUrl="https://superpayacqp.onrender.com/payment-result?paymentRequestId="+payment_request_id,
                resultStatus=ResultStatus.UNKNOWN,
                resultCode="PAYMENT_IN_PROCESS",
                resultMessage="The payment is being processed.",
                paymentStatus=PaymentStatus.PENDING,
                settlementStrategy=SettlementStrategyDTO(settlementCurrency="MYR").model_dump(exclude_none=True)
            )
            
            order = request_dto.order
            if order:
                orderId = str(uuid.uuid4())
                
                # Create Order with null checks
                Order.objects.update_or_create(
                    paymentRequestId=payment_request_id,
                    defaults={
                        'paymentRequestId':payment_request_id,
                        'orderId':orderId,
                        'referenceOrderId': order.referenceOrderId,
                        'orderDescription': order.orderDescription,
                        'orderAmountValue': order.orderAmount.value,
                        'orderAmountCurrency': order.orderAmount.currency,
                        'merchantId': order.merchantId,
                        'shippingName': order.shipping.shippingName.model_dump(exclude_none=True) if order.shipping and order.shipping.shippingName else None,
                        'shippingPhoneNo': order.shipping.shippingPhoneNo if order.shipping else '',
                        'shippingAddress': order.shipping.shippingAddress.model_dump(exclude_none=True) if order.shipping and order.shipping.shippingAddress else None,
                        'shippingCarrier': order.shipping.shippingCarrier if order.shipping else '',
                        'referenceBuyerId': order.buyer.referenceBuyerId if order.buyer else '',
                        'buyerName': order.buyer.buyerName.model_dump(exclude_none=True) if order.buyer and order.buyer.buyerName else None,
                        'buyerPhoneNo': order.buyer.buyerPhoneNo if order.buyer else '',
                        'buyerEmail': order.buyer.buyerEmail if order.buyer else '',
                        'env': order.env.model_dump(exclude_none=True) if order.env else None
                    }
                )
                
                # Create OrderGoods for each item
                if order.goods:
                    for g in order.goods:
                        OrderGoods.objects.update_or_create(
                            orderId=orderId,
                            referenceGoodsId=g.referenceGoodsId or '',
                            defaults={
                                'goodsName': g.goodsName or '',
                                'goodsCategory': g.goodsCategory or '',
                                'goodsBrand': g.goodsBrand or '',
                                'goodsUnitAmountValue': g.goodsUnitAmount.value if g.goodsUnitAmount else None,
                                'goodsUnitAmountCurrency': g.goodsUnitAmount.currency if g.goodsUnitAmount else None,
                                'goodsQuantity': g.goodsQuantity
                            }
                        )

            return payment_request
