import json
import logging
import uuid
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
    AddressDTO
)
from dtos.request import (
    AlipayPayRequestDTO, 
    PaymentMethodDTO, 
    AlipayOrderDTO,
    MerchantInfoDTO,
    RefundRequestDTO
)
from dtos.response import (
    PaymentResponseDTO, 
    CancelPaymentResponseDTO, 
    InquiryPaymentResponseDTO,
    NotifyPaymentResponseDTO,
    AlipayPayResponseDTO,
    RefundResponseDTO
)
from dtos.request import RefundRequestDTO
logger = logging.getLogger(__name__)


class DbService:

    @staticmethod
    @transaction.atomic
    def createApiRecordsWithReqRes(api_url,http_method ,request, response, message_type):
        ApiRecord.objects.create(
            api_url=api_url,
            http_method=http_method,
            request_body=request.model_dump_json(exclude_none=True),
            response_body=response.model_dump_json(),
            message_type=message_type
        )

    @staticmethod
    @transaction.atomic
    def createApiRecordsWithReq(api_url,http_method, request, message_type):
        ApiRecord.objects.create(
            api_url=api_url,
            http_method=http_method,
            request_body=request.model_dump_json(exclude_none=True),
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

            PaymentRequest.objects.update_or_create(
                paymentRequestId=payment_request_id,
                defaults={
                    'acquirerId': response_dto.acquirerId or '',
                    'paymentAmountValue': request_dto.paymentAmount.value,
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
                    existing_settlement.settlementCurrency = response_dto.settlementAmount.currency
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
    def updatePaymentRequestResultByInquiryPayment(response_dto: InquiryPaymentResponseDTO) -> bool:
        """
        Update PaymentRequest fields based on InquiryPaymentResponseDTO.
        Only updates fields that have different values.
        
        Args:
            response_dto: InquiryPaymentResponseDTO from Alipay+ inquiryPayment API
            
        Returns:
            bool: True if any fields were updated, False otherwise
        """
        payment_request_id = response_dto.paymentRequestId
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
        
        # Update result fields from paymentResult (primary) or result (fallback)
        result = response_dto.paymentResult or response_dto.result
        if result:
            result_status = result.resultStatus.value if hasattr(result.resultStatus, 'value') else result.resultStatus
            update_if_different('resultStatus', result_status, payment_request.resultStatus)
            update_if_different('resultCode', result.resultCode, payment_request.resultCode)
            update_if_different('resultMessage', result.resultMessage, payment_request.resultMessage)
            
            # Update paymentStatus based on resultStatus
            new_payment_status = None
            match result.resultStatus:
                case ResultStatus.SUCCESS:
                    new_payment_status = PaymentStatus.SUCCESS.value
                case ResultStatus.FAILURE:
                    new_payment_status = PaymentStatus.FAILED.value
                case ResultStatus.UNKNOWN:
                    new_payment_status = PaymentStatus.PENDING.value
            
            if new_payment_status:
                update_if_different('paymentStatus', new_payment_status, payment_request.paymentStatus)
    
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
                existing_settlement.settlementCurrency = response_dto.settlementAmount.currency
                existing_settlement.quoteId = quote_id
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
                    settlementCurrency=response_dto.settlementAmount.currency,
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
            merchant.currency=request.currency
            merchant.save()

        else:
            Merchant.objects.create(
            merchantId=request.referenceMerchantId if request.referenceMerchantId else str(uuid.uuid4()),
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
    def createRefundRecord (request_dto:RefundRequestDTO, response_dto: RefundResponseDTO)-> RefundRecord:
        paymentRequestId=request_dto.paymentRequestId
        paymentId=request_dto.paymentId
        if not request_dto.paymentRequestId and request_dto.paymentId:
            paymentRequestId=PaymentRequest.objects.get(paymentId=request_dto.paymentId).paymentRequestId
        if not request_dto.paymentId and request_dto.paymentRequestId:
            paymentId=PaymentRequest.objects.get(paymentRequestId=request_dto.paymentRequestId).paymentId

        # Extract result fields from response if available
        resultStatus = None
        resultCode = None
        resultMessage = None
        if response_dto :
            resultStatus = response_dto.result.resultStatus
            resultCode = response_dto.result.resultCode
            resultMessage = response_dto.result.resultMessage

        record=RefundRecord.objects.create(
                    refundRequestId=request_dto.refundRequestId,
                    paymentRequestId=paymentRequestId,
                    paymentId=paymentId,
                    refundAmountValue=request_dto.refundAmount.value,
                    refundAmountCurrency=request_dto.refundAmount.currency,
                    refundReason=request_dto.refundReason or None,
                    resultStatus=resultStatus,
                    resultCode=resultCode,
                    resultMessage=resultMessage
                )
        return record
