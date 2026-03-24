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
from apps.orders.models import Order, OrderGoods
from apps.merchants.merchants_models import Merchant
from apps.refunds.refund_models import RefundRecord

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class PaymentListView(APIView):
    """
    GET /api/query/payments
    Returns all payment request records joined with Orders table
    """
    
    def get(self, request):
        try:
            # Query all payment requests with related orders
            payment_requests = PaymentRequest.objects.all().order_by('-created_at')
            
            payments_data = []
            for pr in payment_requests:
                # Get related order
                order = Order.objects.filter(paymentRequestId=pr.paymentRequestId).first()
                
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
                    'order': None
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
                    }
                
                payments_data.append(payment_dict)
            
            return Response({
                'payments': payments_data,
                'total': len(payments_data)
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
                    'merchantAddress': merchant.merchantAddress,
                    'store': merchant.store,
                    'registrationDetailLegalName': merchant.registrationDetailLegalName,
                    'registrationDetailRegistrationType': merchant.registrationDetailRegistrationType,
                    'registrationDetailRegistrationNo': merchant.registrationDetailRegistrationNo,
                    'registrationDetailRegistrationAddress': merchant.registrationDetailRegistrationAddress,
                    'registrationDetailBusinessType': merchant.registrationDetailBusinessType,
                    'websites': merchant.websites,
                    'productCodes': merchant.productCodes,
                    'registrationNotifyUrl': merchant.registrationNotifyUrl,
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
                        'merchantAddress': m.merchantAddress,
                        'store': m.store,
                        'registrationDetailLegalName': m.registrationDetailLegalName,
                        'registrationDetailRegistrationType': m.registrationDetailRegistrationType,
                        'registrationDetailRegistrationNo': m.registrationDetailRegistrationNo,
                        'registrationDetailRegistrationAddress': m.registrationDetailRegistrationAddress,
                        'registrationDetailBusinessType': m.registrationDetailBusinessType,
                        'websites': m.websites,
                        'productCodes': m.productCodes,
                        'registrationNotifyUrl': m.registrationNotifyUrl,
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
class MerchantUpdateView(APIView):
    """
    PUT /api/query/merchants/update
    Update a specific merchant by ID
    Query params: merchantId (required)
    Request body: fields to update
    """
    
    def put(self, request):
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
            
            # Update fields if provided in request body
            data = request.data
            
            if 'merchantName' in data:
                merchant.merchantName = data['merchantName']
            if 'merchantDisplayName' in data:
                merchant.merchantDisplayName = data['merchantDisplayName']
            if 'merchantRegisterDate' in data:
                merchant.merchantRegisterDate = data['merchantRegisterDate']
            if 'merchantMCC' in data:
                merchant.merchantMCC = data['merchantMCC']
            if 'merchantAddress' in data:
                merchant.merchantAddress = data['merchantAddress']
            if 'store' in data:
                merchant.store = data['store']
            if 'registrationDetailLegalName' in data:
                merchant.registrationDetailLegalName = data['registrationDetailLegalName']
            if 'registrationDetailRegistrationType' in data:
                merchant.registrationDetailRegistrationType = data['registrationDetailRegistrationType']
            if 'registrationDetailRegistrationNo' in data:
                merchant.registrationDetailRegistrationNo = data['registrationDetailRegistrationNo']
            if 'registrationDetailRegistrationAddress' in data:
                merchant.registrationDetailRegistrationAddress = data['registrationDetailRegistrationAddress']
            if 'registrationDetailBusinessType' in data:
                merchant.registrationDetailBusinessType = data['registrationDetailBusinessType']
            if 'websites' in data:
                merchant.websites = data['websites']
            if 'productCodes' in data:
                merchant.productCodes = data['productCodes']
            if 'registrationNotifyUrl' in data:
                merchant.registrationNotifyUrl = data['registrationNotifyUrl']
            
            merchant.save()
            
            return Response({
                'message': 'Merchant updated successfully',
                'merchant': {
                    'merchantId': merchant.merchantId,
                    'merchantName': merchant.merchantName,
                    'merchantDisplayName': merchant.merchantDisplayName,
                    'merchantRegisterDate': merchant.merchantRegisterDate.isoformat() if merchant.merchantRegisterDate else None,
                    'merchantMCC': merchant.merchantMCC,
                    'merchantAddress': merchant.merchantAddress,
                    'store': merchant.store,
                    'registrationDetailLegalName': merchant.registrationDetailLegalName,
                    'registrationDetailRegistrationType': merchant.registrationDetailRegistrationType,
                    'registrationDetailRegistrationNo': merchant.registrationDetailRegistrationNo,
                    'registrationDetailRegistrationAddress': merchant.registrationDetailRegistrationAddress,
                    'registrationDetailBusinessType': merchant.registrationDetailBusinessType,
                    'websites': merchant.websites,
                    'productCodes': merchant.productCodes,
                    'registrationNotifyUrl': merchant.registrationNotifyUrl,
                    'created_at': merchant.created_at.isoformat() if merchant.created_at else None,
                    'updated_at': merchant.updated_at.isoformat() if merchant.updated_at else None,
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error updating merchant: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class MerchantDeleteView(APIView):
    """
    DELETE /api/query/merchants/delete
    Delete a specific merchant by ID
    Query params: merchantId (required)
    """
    
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
