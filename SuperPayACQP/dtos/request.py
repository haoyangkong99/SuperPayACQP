"""
Request DTOs
"""
from dtos import AmountDTO, BaseRequestDTO
from pydantic import BaseModel
from typing import Optional, List


class PaymentFactorDTO(BaseModel):
    """Payment factor DTO"""
    isInStorePayment: Optional[bool] = False
    isCashierPayment: Optional[bool] = False
    inStorePaymentScenario: Optional[str] = None


class NameDTO(BaseModel):
    """Name DTO"""
    middleName: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    fullName: Optional[str] = None


class AddressDTO(BaseModel):
    """Address DTO"""
    region: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    zipCode: Optional[str] = None


class ShippingDTO(BaseModel):
    """Shipping DTO"""
    shippingName: Optional[NameDTO] = None
    shippingPhoneNo: Optional[str] = None
    shippingAddress: Optional[AddressDTO] = None
    shippingCarrier: Optional[str] = None


class BuyerDTO(BaseModel):
    """Buyer DTO"""
    referenceBuyerId: Optional[str] = None
    buyerName: Optional[NameDTO] = None
    buyerPhoneNo: Optional[str] = None
    buyerEmail: Optional[str] = None


class EnvDTO(BaseModel):
    """Environment DTO"""
    terminalType: Optional[str] = None
    osType: Optional[str] = None
    deviceTokenId: Optional[str] = None
    cookieId: Optional[str] = None
    clientIp: Optional[str] = None
    userAgent: Optional[str] = None
    storeTerminalId: Optional[str] = None
    storeTerminalRequestTime: Optional[str] = None


class GoodsDTO(BaseModel):
    """Goods DTO"""
    referenceGoodsId: Optional[str] = None
    goodsName: Optional[str] = None
    goodsCategory: Optional[str] = None
    goodsBrand: Optional[str] = None
    goodsUnitAmount: Optional[AmountDTO] = None
    goodsQuantity: Optional[int] = None


class OrderDTO(BaseModel):
    """Order DTO for place order request"""
    referenceOrderId: Optional[str] = None
    orderDescription: Optional[str] = None
    orderAmount: AmountDTO
    paymentFactor: Optional[PaymentFactorDTO] = None
    merchantId: str
    goods: Optional[List[GoodsDTO]] = None
    shipping: Optional[ShippingDTO] = None
    buyer: Optional[BuyerDTO] = None
    env: Optional[EnvDTO] = None


class PlaceOrderRequestDTO(BaseRequestDTO):
    """Place order request DTO"""
    order: OrderDTO


class CancelPaymentRequestDTO(BaseRequestDTO):
    """Cancel payment request DTO"""
    paymentId: str
    paymentRequestId: str


class RefundRequestDTO(BaseRequestDTO):
    """Refund request DTO"""
    paymentRequestId: str
    paymentId: str
    refundRequestId: str
    refundAmount: AmountDTO
    refundReason: Optional[str] = None


class InquiryPaymentRequestDTO(BaseRequestDTO):
    """Inquiry payment request DTO"""
    paymentId: Optional[str] = None
    paymentRequestId: str
