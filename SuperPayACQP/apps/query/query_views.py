"""
Query API Views
Endpoints for querying payment, merchant, and refund records
"""
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from apps.payments.payments_models import PaymentRequest, Settlement
from apps.orders.orders_models import Order, OrderGoods
from apps.merchants.merchants_models import Merchant
from apps.refunds.refund_models import RefundRecord

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class PaymentListView(APIView):
    """
    GET /api/query/payments
    Returns all payment request records joined with Orders table
    
    Query Parameters:
    - page: Page number (default: 1)
    - page_size: Number of items per page (default: 10, max: 100)
    - search: Search term for order ID, payment request ID, merchant ID, or payment ID
    - status: Filter by result status (S, F, U)
    - scenario: Filter by in-store payment scenario (OrderCode, PaymentCode)
    """
    
    def get(self, request):
        try:
            # Get pagination parameters
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            # Get filter parameters
            search = request.query_params.get('search', '').strip()
            status_filter = request.query_params.get('status', '').strip()
            scenario_filter = request.query_params.get('scenario', '').strip()
            
            # Validate pagination parameters
            if page < 1:
                page = 1
            if page_size < 1:
                page_size = 10
            if page_size > 100:
                page_size = 100
            
            # Query all payment requests with related orders
            payment_requests = PaymentRequest.objects.all().order_by('-created_at')
            
            # Apply status filter
            if status_filter:
                payment_requests = payment_requests.filter(resultStatus=status_filter)
            
            # Apply scenario filter
            if scenario_filter:
                payment_requests = payment_requests.filter(inStorePaymentScenario=scenario_filter)
            
            # Apply search filter
            if search:
                # Get payment request IDs that match via order
                matching_order_ids = Order.objects.filter(
                    referenceOrderId__icontains=search
                ).values_list('paymentRequestId', flat=True)
                
                matching_merchant_ids = Order.objects.filter(
                    merchantId__icontains=search
                ).values_list('paymentRequestId', flat=True)
                
                # Filter by payment request ID, payment ID, or related order IDs
                from django.db.models import Q
                payment_requests = payment_requests.filter(
                    Q(paymentRequestId__icontains=search) |
                    Q(paymentId__icontains=search) |
                    Q(paymentRequestId__in=matching_order_ids) |
                    Q(paymentRequestId__in=matching_merchant_ids)
                )
            
            # Get total count before pagination
            total_count = payment_requests.count()
            
            # Calculate pagination
            total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            
            # Apply pagination
            payment_requests = payment_requests[start_index:end_index]
            
            payments_data = []
            for pr in payment_requests:
                # Get related order
                order = Order.objects.filter(paymentRequestId=pr.paymentRequestId).first()
                
                payment_dict = {
                    'paymentRequestId': pr.paymentRequestId,
                    'acquirerId': pr.acquirerId,
                    'paymentAmountValue': pr.paymentAmountValue,
                    'paymentAmountCurrency': pr.paymentAmountCurrency,
                    'paymentMethodId': pr.paymentMethodId,
                    'customerId': pr.customerId,
                    'isInStorePayment': pr.isInStorePayment,
                    'isCashierPayment': pr.isCashierPayment,
                    'inStorePaymentScenario': pr.inStorePaymentScenario,
                    'paymentId': pr.paymentId,
                    'paymentTime': pr.paymentTime.isoformat() if pr.paymentTime else None,
                    'walletBrandName': pr.walletBrandName,
                    'mppPaymentId': pr.mppPaymentId,
                    'resultStatus': pr.resultStatus,
                    'resultCode': pr.resultCode,
                    'resultMessage': pr.resultMessage,
                    'paymentStatus': pr.paymentStatus,
                    'created_at': pr.created_at.isoformat() if pr.created_at else None,
                    'updated_at': pr.updated_at.isoformat() if pr.updated_at else None,
                    'order': None
                }
                
                if order:
                    payment_dict['orderId'] = order.orderId
                    payment_dict['referenceOrderId'] = order.referenceOrderId
                    payment_dict['orderDescription'] = order.orderDescription
                    payment_dict['orderAmountValue'] = order.orderAmountValue
                    payment_dict['orderAmountCurrency'] = order.orderAmountCurrency
                    payment_dict['merchantId'] = order.merchantId
                
                payments_data.append(payment_dict)
            
            return Response({
                'payments': payments_data,
                'total': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_previous': page > 1
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching payments: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class PaymentDetailView(APIView):
    """
    GET /api/query/payments/detail
    Returns a specific payment request joined with Settlement, Orders, and OrderGoods tables
    Query params: paymentRequestId or paymentId
    """
    
    def get(self, request):
        payment_request_id = request.query_params.get('paymentRequestId')
        payment_id = request.query_params.get('paymentId')
        
        if not payment_request_id and not payment_id:
            return Response({
                'error': 'Either paymentRequestId or paymentId is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Find payment request
            if payment_request_id:
                pr = PaymentRequest.objects.filter(paymentRequestId=payment_request_id).first()
            else:
                pr = PaymentRequest.objects.filter(paymentId=payment_id).first()
            
            if not pr:
                return Response({
                    'error': 'Payment request not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get related settlement
            settlement = Settlement.objects.filter(paymentRequestId=pr.paymentRequestId).first()
            
            # Get related order
            order = Order.objects.filter(paymentRequestId=pr.paymentRequestId).first()
            
            # Get order goods if order exists
            order_goods = []
            if order:
                goods = OrderGoods.objects.filter(orderId=order.orderId)
                for g in goods:
                    order_goods.append({
                        'id': g.id,
                        'orderId': g.orderId,
                        'referenceGoodsId': g.referenceGoodsId,
                        'goodsName': g.goodsName,
                        'goodsCategory': g.goodsCategory,
                        'goodsBrand': g.goodsBrand,
                        'goodsUnitAmountValue': g.goodsUnitAmountValue,
                        'goodsUnitAmountCurrency': g.goodsUnitAmountCurrency,
                        'goodsQuantity': g.goodsQuantity,
                        'created_at': g.created_at.isoformat() if g.created_at else None,
                        'updated_at': g.updated_at.isoformat() if g.updated_at else None,
                    })
            
            # Build response
            payment_dict = {
                'paymentRequestId': pr.paymentRequestId,
                'acquirerId': pr.acquirerId,
                'paymentAmountValue': pr.paymentAmountValue,
                'paymentAmountCurrency': pr.paymentAmountCurrency,
                'paymentMethodType': pr.paymentMethodType,
                'paymentMethodId': pr.paymentMethodId,
                'customerId': pr.customerId,
                'paymentMethodMetaData': pr.paymentMethodMetaData,
                'isInStorePayment': pr.isInStorePayment,
                'isCashierPayment': pr.isCashierPayment,
                'inStorePaymentScenario': pr.inStorePaymentScenario,
                'paymentExpiryTime': pr.paymentExpiryTime.isoformat() if pr.paymentExpiryTime else None,
                'paymentNotifyUrl': pr.paymentNotifyUrl,
                'paymentRedirectUrl': pr.paymentRedirectUrl,
                'splitSettlementId': pr.splitSettlementId,
                'settlementStrategy': pr.settlementStrategy,
                'paymentId': pr.paymentId,
                'paymentTime': pr.paymentTime.isoformat() if pr.paymentTime else None,
                'pspId': pr.pspId,
                'walletBrandName': pr.walletBrandName,
                'mppPaymentId': pr.mppPaymentId,
                'customsDeclarationAmountValue': pr.customsDeclarationAmountValue,
                'customsDeclarationAmountCurrency': pr.customsDeclarationAmountCurrency,
                'resultStatus': pr.resultStatus,
                'resultCode': pr.resultCode,
                'resultMessage': pr.resultMessage,
                'paymentStatus': pr.paymentStatus,
                'created_at': pr.created_at.isoformat() if pr.created_at else None,
                'updated_at': pr.updated_at.isoformat() if pr.updated_at else None,
                'settlement': None,
                'order': None
            }
            
            if settlement:
                payment_dict['settlement'] = {
                    'settlementId': settlement.settlementId,
                    'paymentRequestId': settlement.paymentRequestId,
                    'settlementAmountValue': settlement.settlementAmountValue,
                    'settlementCurrency': settlement.settlementCurrency,
                    'quoteId': settlement.quoteId,
                    'quotePrice': str(settlement.quotePrice) if settlement.quotePrice else None,
                    'quoteCurrencyPair': settlement.quoteCurrencyPair,
                    'quoteStartTime': settlement.quoteStartTime.isoformat() if settlement.quoteStartTime else None,
                    'quoteExpiryTime': settlement.quoteExpiryTime.isoformat() if settlement.quoteExpiryTime else None,
                    'quoteUnit': settlement.quoteUnit,
                    'baseCurrency': settlement.baseCurrency,
                    'created_at': settlement.created_at.isoformat() if settlement.created_at else None,
                    'updated_at': settlement.updated_at.isoformat() if settlement.updated_at else None,
                }
            
            if order:
                payment_dict['order'] = {
                    'orderId': order.orderId,
                    'paymentRequestId': order.paymentRequestId,
                    'referenceOrderId': order.referenceOrderId,
                    'orderDescription': order.orderDescription,
                    'orderAmountValue': order.orderAmountValue,
                    'orderAmountCurrency': order.orderAmountCurrency,
                    'merchantId': order.merchantId,
                    'shippingName': order.shippingName,
                    'shippingPhoneNo': order.shippingPhoneNo,
                    'shippingAddress': order.shippingAddress,
                    'shippingCarrier': order.shippingCarrier,
                    'referenceBuyerId': order.referenceBuyerId,
                    'buyerName': order.buyerName,
                    'buyerPhoneNo': order.buyerPhoneNo,
                    'buyerEmail': order.buyerEmail,
                    'env': order.env,
                    'indirectAcquirer': order.indirectAcquirer,
                    'created_at': order.created_at.isoformat() if order.created_at else None,
                    'updated_at': order.updated_at.isoformat() if order.updated_at else None,
                    'goods': order_goods
                }
            
            return Response({
                'payment': payment_dict
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching payment detail: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class MerchantQueryView(APIView):
    """
    GET /api/query/merchants
    Returns all merchants or a specific merchant by ID
    Query params: merchantId (optional)
    """
    
    def get(self, request):
        merchant_id = request.query_params.get('merchantId')
        
        try:
            if merchant_id:
                # Get specific merchant
                merchant = Merchant.objects.filter(merchantId=merchant_id).first()
                if not merchant:
                    return Response({
                        'error': 'Merchant not found'
                    }, status=status.HTTP_404_NOT_FOUND)
                
                merchants_data = [{
                    'merchantId': merchant.merchantId,
                    'merchantName': merchant.merchantName,
                    'merchantDisplayName': merchant.merchantDisplayName,
                    'merchantRegisterDate': merchant.merchantRegisterDate.isoformat() if merchant.merchantRegisterDate else None,
                    'merchantMCC': merchant.merchantMCC,
                    'currency': merchant.currency,
                    'merchantAddress': merchant.merchantAddress,
                    'store': merchant.store,
                    'created_at': merchant.created_at.isoformat() if merchant.created_at else None,
                    'updated_at': merchant.updated_at.isoformat() if merchant.updated_at else None,
                }]
            else:
                # Get all merchants
                merchants = Merchant.objects.all().order_by('-created_at')
                merchants_data = []
                for m in merchants:
                    merchants_data.append({
                        'merchantId': m.merchantId,
                        'merchantName': m.merchantName,
                        'merchantDisplayName': m.merchantDisplayName,
                        'merchantRegisterDate': m.merchantRegisterDate.isoformat() if m.merchantRegisterDate else None,
                        'merchantMCC': m.merchantMCC,
                        'currency': m.currency,
                        'merchantAddress': m.merchantAddress,
                        'store': m.store,
                        'created_at': m.created_at.isoformat() if m.created_at else None,
                        'updated_at': m.updated_at.isoformat() if m.updated_at else None,
                    })
            
            return Response({
                'merchants': merchants_data,
                'total': len(merchants_data)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching merchants: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@method_decorator(csrf_exempt, name='dispatch')
class RefundQueryView(APIView):
    """
    GET /api/query/refunds
    Returns refund records based on query parameters
    Query params: paymentRequestId, refundRequestId, or paymentId
    """
    
    def get(self, request):
        payment_request_id = request.query_params.get('paymentRequestId')
        refund_request_id = request.query_params.get('refundRequestId')
        payment_id = request.query_params.get('paymentId')
        
        try:
            refunds = RefundRecord.objects.all()
            
            # Apply filters
            if refund_request_id:
                refunds = refunds.filter(refundRequestId=refund_request_id)
            if payment_request_id:
                refunds = refunds.filter(paymentRequestId=payment_request_id)
            if payment_id:
                refunds = refunds.filter(paymentId=payment_id)
            
            refunds = refunds.order_by('-created_at')
            
            refunds_data = []
            for r in refunds:
                refunds_data.append({
                    'refundRequestId': r.refundRequestId,
                    'paymentRequestId': r.paymentRequestId,
                    'paymentId': r.paymentId,
                    'refundAmountValue': r.refundAmountValue,
                    'refundAmountCurrency': r.refundAmountCurrency,
                    'refundReason': r.refundReason,
                    'resultStatus': r.resultStatus,
                    'resultCode': r.resultCode,
                    'resultMessage': r.resultMessage,
                    'created_at': r.created_at.isoformat() if r.created_at else None,
                    'updated_at': r.updated_at.isoformat() if r.updated_at else None,
                })
            
            return Response({
                'refunds': refunds_data,
                'total': len(refunds_data)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching refunds: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
