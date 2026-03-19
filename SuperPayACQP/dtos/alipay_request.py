"""
Alipay+ Request DTOs
"""
from dtos import AmountDTO, BaseRequestDTO
from pydantic import BaseModel
from typing import Optional, List


class PaymentMethodDTO(BaseModel):
    """Payment method DTO"""
    paymentMethodType: str = "CONNECT_WALLET"
    paymentMethodId: Optional[str] = None
    customerId: Optional[str] = None
    paymentMethodMetaData: Optional[dict] = None


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
    storeAddress: Optional[dict] = None


class MerchantInfoDTO(BaseModel):
    """Merchant info DTO"""
    referenceMerchantId: Optional[str] = None
    merchantName: Optional[str] = None
    merchantDisplayName: Optional[str] = None
    merchantRegisterDate: Optional[str] = None
    merchantMCC: Optional[str] = None
    merchantAddress: Optional[dict] = None
    store: Optional[StoreDTO] = None


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
    goods: Optional[List[dict]] = None
    shipping: Optional[dict] = None
    buyer: Optional[dict] = None
    env: Optional[dict] = None
    indirectAcquirer: Optional[IndirectAcquirerDTO] = None


class AlipayPayRequestDTO(BaseRequestDTO):
    """Alipay+ pay request DTO"""
    paymentRequestId: str
    paymentAmount: AmountDTO
    paymentMethod: PaymentMethodDTO
    paymentFactor: Optional[dict] = None
    paymentExpiryTime: str
    paymentNotifyUrl: Optional[str] = None
    paymentRedirectUrl: Optional[str] = None
    splitSettlementId: Optional[str] = None
    settlementStrategy: Optional[SettlementStrategyDTO] = None
    order: AlipayOrderDTO

    def to_alipay_dict(self) -> dict:
        """Convert to dictionary for Alipay+ API"""
        return self.model_dump(exclude_none=True)
