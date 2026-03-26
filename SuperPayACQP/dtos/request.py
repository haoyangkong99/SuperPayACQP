"""
Request DTOs
"""
from dtos import AmountDTO, BaseRequestDTO
from pydantic import BaseModel
from typing import Optional, List
from dtos.response import SettlementQuoteDTO
from utils.constants import Result

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
    referenceOrderId: Optional[str]=None 
    orderDescription: str 
    orderAmount: AmountDTO
    merchantId: str
    goods: Optional[List[GoodsDTO]] = None
    shipping: Optional[ShippingDTO] = None
    buyer: Optional[BuyerDTO] = None
    env: Optional[EnvDTO] = None


class PaymentMethodDTO(BaseModel):
    """Payment method DTO"""
    paymentMethodType: str = "CONNECT_WALLET"
    paymentMethodId: Optional[str] = None
    customerId: Optional[str] = None
    paymentMethodMetaData: Optional[dict] = None


class PlaceOrderRequestDTO(BaseRequestDTO):
    """Place order request DTO"""
    order: OrderDTO
    paymentFactor: PaymentFactorDTO
    paymentAmount: AmountDTO
    paymentMethod: PaymentMethodDTO 


class CancelPaymentRequestDTO(BaseRequestDTO):
    """Cancel payment request DTO"""
    paymentId: Optional[str] = None
    paymentRequestId: Optional[str] = None


class RefundRequestDTO(BaseRequestDTO):
    """Refund request DTO"""
    paymentRequestId: Optional[str] = None
    paymentId: Optional[str] = None
    refundRequestId: Optional[str] = None
    refundAmount: AmountDTO
    refundReason: Optional[str] = None


class InquiryPaymentRequestDTO(BaseRequestDTO):
    """Inquiry payment request DTO"""
    paymentId: Optional[str] = None
    paymentRequestId: Optional[str] = None


class SettlementStrategyDTO(BaseModel):
    """Settlement strategy DTO"""
    settlementCurrency: Optional[str] = None


class StoreDTO(BaseModel):
    """Store DTO"""
    referenceStoreId: Optional[str] = None
    storeName: Optional[str] = None
    storeMCC: Optional[str] = None
    storeDisplayName: Optional[str] = None
    storeTerminalId: Optional[str] = None
    storeOperatorId: Optional[str] = None
    storePhoneNo: Optional[str] = None
    storeAddress: Optional[AddressDTO] = None


class MerchantInfoDTO(BaseModel):
    """Merchant info DTO"""
    referenceMerchantId: Optional[str] = None
    merchantName: str
    merchantDisplayName: str
    merchantRegisterDate: Optional[str] = None
    merchantMCC: str
    merchantAddress: AddressDTO
    store: Optional[StoreDTO] = None
    currency: str


class IndirectAcquirerDTO(BaseModel):
    """Indirect acquirer DTO"""
    referenceAcquirerId: Optional[str] = None
    acquirerName: Optional[str] = None
    acquirerAddress: Optional[dict] = None


class AlipayOrderDTO(BaseModel):
    """Alipay+ order DTO"""
    referenceOrderId: Optional[str] = None
    orderDescription: Optional[str] = None
    orderAmount: AmountDTO
    merchant: Optional[MerchantInfoDTO] = None
    goods: Optional[List[GoodsDTO]] = None
    shipping: Optional[ShippingDTO] = None
    buyer: Optional[BuyerDTO] = None
    env: Optional[EnvDTO] = None
    indirectAcquirer: Optional[IndirectAcquirerDTO] = None


class AlipayPayRequestDTO(BaseRequestDTO):
    """Alipay+ pay request DTO"""
    paymentRequestId: str
    paymentAmount: AmountDTO
    paymentMethod: PaymentMethodDTO
    paymentFactor: PaymentFactorDTO
    paymentExpiryTime: str
    paymentNotifyUrl: Optional[str] = None
    paymentRedirectUrl: Optional[str] = None
    splitSettlementId: Optional[str] = None
    settlementStrategy: Optional[SettlementStrategyDTO] = None
    order: AlipayOrderDTO

    def to_alipay_dict(self) -> dict:
        """Convert to dictionary for Alipay+ API"""
        return self.model_dump(exclude_none=True)

class NotifyPaymentRequestDTO(BaseModel):
    """Notify payment request DTO from Alipay+ callback"""
    paymentResult: Result
    acquirerId: str
    pspId: Optional[str] = None
    paymentRequestId: str
    paymentId: Optional[str] = None
    customerId: Optional[str] = None
    walletBrandName: Optional[str] = None
    paymentAmount: AmountDTO
    paymentTime: Optional[str] = None
    settlementAmount: Optional[AmountDTO] = None
    settlementQuote: Optional[SettlementQuoteDTO] = None
    customsDeclarationAmount: Optional[AmountDTO] = None
    mppPaymentId: Optional[str] = None

class RegistrationDetail(BaseModel):
    legalName: str
    registrationType: str
    registrationNo: Optional[str] = None
    registrationAddress: AddressDTO
    businessType: str

class WebSite(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    desc: Optional[str] = None
    websiteType: Optional[str] = None

class MerchantRegistrationInfo(BaseModel):
    referenceMerchantId: Optional[str] = None
    merchantDisplayName: Optional[str] = None
    merchantMCC: Optional[str] = None
    websites: Optional[List[WebSite]] = None
    registrationDetail: Optional[RegistrationDetail] = None

class StoreRegistrationInfo(BaseModel):
    referenceStoreId: Optional[str] = None
    storeName: Optional[str] = None
    storeMCC: Optional[str] = None
    storeAddress: Optional[AddressDTO] = None

class RegistrationRequestDTO(BaseRequestDTO):
    registrationRequestId: str
    productCodes: List[str]
    merchantInfo: MerchantRegistrationInfo
    storeInfo: Optional[StoreRegistrationInfo] = None
    registrationNotifyUrl: Optional[str] = None
    passThroughInfo: Optional[str] = None


class GoodsUnitAmountDTO(BaseModel):
    """Goods unit amount DTO"""
    value: int
    currency: str = 'MYR'


class GoodsCatalogItemRequestDTO(BaseRequestDTO):
    """Goods catalog item request DTO for upsert operations"""
    goodsId: Optional[str] = None
    goodsName: str
    goodsCategory: Optional[str] = None
    goodsBrand: Optional[str] = None
    goodsUnitAmountValue: int
    goodsUnitAmountCurrency: Optional[str] = 'MYR'
    stockQuantity: Optional[int] = 0
    taxRate: Optional[float] = 0.00
