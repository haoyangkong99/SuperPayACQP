"""
Response DTOs
"""
from __future__ import annotations
from dtos import BaseResponseDTO, AmountDTO
from pydantic import BaseModel
from typing import Optional, List
from utils.constants import Result

from dtos.request import OrderDTO,PaymentFactorDTO,SettlementStrategyDTO

class SettlementQuoteDTO(BaseModel):
    """Settlement quote DTO"""
    quoteId: Optional[str] = None
    quoteCurrencyPair: Optional[str] = None
    quotePrice: Optional[float] = None
    quoteStartTime: Optional[str] = None
    quoteExpiryTime: Optional[str] = None
    quoteUnit: Optional[str] = None
    baseCurrency: Optional[str] = None


class PaymentResponseDTO(BaseResponseDTO):
    """Payment response DTO"""
    paymentRequestId: Optional[str] = None 
    paymentId: Optional[str] = None
    paymentTime: Optional[str] = None
    paymentExpireTime: Optional[str] = None
    paymentAmount: Optional[AmountDTO] = None
    customerId: Optional[str] = None
    pspId: Optional[str] = None
    walletBrandName: Optional[str] = None
    mppPaymentId: Optional[str] = None
    orderCodeForm: Optional[dict] = None
    paymentUrl:Optional[str]=None
    schemeUrl:Optional[str] = None
    applinkUrl:Optional[str] = None
    normalUrl:Optional[str] = None
    appIdentifier:Optional[str] = None

class PrivatePlaceOrderResponseDTO(BaseResponseDTO):
    """Payment response DTO"""
    paymentRequestId: Optional[str] = None 
    paymentExpireTime: Optional[str] = None
    paymentAmount: Optional[AmountDTO] = None


class AlipayPayResponseDTO(BaseResponseDTO):
    """Payment response DTO"""
    acquirerId: Optional[str] = None
    paymentId: Optional[str] = None
    paymentTime: Optional[str] = None
    paymentAmount: Optional[AmountDTO] = None
    customerId: Optional[str] = None
    pspId: Optional[str] = None
    walletBrandName: Optional[str] = None
    settlementAmount: Optional[AmountDTO] = None
    settlementQuote: Optional[SettlementQuoteDTO] = None
    customsDeclarationAmount: Optional[AmountDTO] = None
    mppPaymentId: Optional[str] = None
    orderCodeForm: Optional[dict] = None
    paymentUrl:Optional[str]=None
    schemeUrl:Optional[str] = None
    applinkUrl:Optional[str] = None
    normalUrl:Optional[str] = None
    appIdentifier:Optional[str] = None

class CancelPaymentResponseDTO(BaseResponseDTO):
    """Cancel payment response DTO"""
    pspId: Optional[str] = None
    acquirerId: Optional[str] = None


class RefundResponseDTO(BaseResponseDTO):
    """Refund response DTO"""
    acquirerId: Optional[str] = None
    pspId: Optional[str] = None
    refundId: Optional[str] = None
    refundTime: Optional[str] = None
    refundAmount: Optional[AmountDTO] = None
    settlementAmount: Optional[AmountDTO] = None
    settlementQuote: Optional[dict] = None


class TransactionResultDTO(BaseModel):
    """Transaction result DTO"""
    resultCode: Optional[str] = None
    resultStatus: Optional[str] = None
    resultMessage: Optional[str] = None


class TransactionDTO(BaseModel):
    """Transaction DTO"""
    transactionResult: Optional[Result] = None
    transactionId: Optional[str] = None
    transactionRequestId: Optional[str] = None
    transactionAmount: Optional[AmountDTO] = None
    transactionTime: Optional[str] = None
    transactionType: Optional[str] = None
    transactionStatus: Optional[str] = None


class InquiryPaymentResponseDTO(BaseResponseDTO):
    """Inquiry payment response DTO"""
    paymentResult: Optional[Result] = None
    acquirerId: Optional[str] = None
    pspId: Optional[str] = None
    paymentRequestId: Optional[str] = None
    paymentId: Optional[str] = None
    paymentAmount: Optional[AmountDTO] = None
    paymentTime: Optional[str] = None
    customerId: Optional[str] = None
    walletBrandName: Optional[str] = None
    settlementAmount: Optional[AmountDTO] = None
    settlementQuote: Optional[SettlementQuoteDTO] = None
    customsDeclarationAmount: Optional[AmountDTO] = None
    mppPaymentId: Optional[str] = None
    transactions: Optional[List[TransactionDTO]] = None


class NotifyPaymentResponseDTO(BaseResponseDTO):
    """Notify payment response DTO"""
    pass  # Only contains result field

class RegistrationRequestDTO(BaseResponseDTO):
    passThroughInfo: Optional[str] = None


class GoodsCatalogItemDTO(BaseModel):
    """Goods catalog item DTO for response"""
    goodsId: str
    goodsName: str
    goodsCategory: str
    goodsBrand: str
    goodsUnitAmountValue: int
    goodsUnitAmountCurrency: str
    stockQuantity: int
    taxRate: float
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class GoodsCatalogUpsertResponseDTO(BaseResponseDTO):
    """Goods catalog upsert response DTO"""
    goodsId: str
    action: str  # 'created' or 'updated'


class GoodsCatalogListResponseDTO(BaseResponseDTO):
    """Goods catalog list response DTO"""
    count: int
    goods: List[GoodsCatalogItemDTO]


class GoodsCatalogDetailResponseDTO(BaseResponseDTO):
    """Goods catalog detail response DTO"""
    goodsId: str
    goodsName: str
    goodsCategory: str
    goodsBrand: str
    goodsUnitAmountValue: int
    goodsUnitAmountCurrency: str
    stockQuantity: int
    taxRate: float
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
class EntryCodeConfirmResponseDTO(BaseResponseDTO):
    """Goods catalog detail response DTO"""
    paymentRequestId: str
    paymentUrl:Optional[str] = None

class Logo (BaseModel):
    logoName: str
    logoUrl: Optional[str]=None

class PaymentOption(BaseModel):
    paymentMethodType: str
    paymentMethodCategory: str
    enabled: bool
    disableReason: Optional[str]=None
    logo: Optional[Logo]=None
    brandName: Optional[str]=None
    paymentOptionDetail: Optional[PaymentOptionDetail]=None
class WalletFeature (BaseModel):
    supportCodeScan: bool
    supportCashierRedirection:bool
class Wallet(BaseModel):
    walletName: str
    walletBrandName: Optional[str]=None
    walletLogo: Optional[Logo]=None
    walletRegion: Optional[str]=None
    walletFeature: Optional[WalletFeature]=None
class WalletPaymentOptionDetail (BaseModel):
    supportWallets: List[Wallet]
class PaymentOptionDetail(BaseModel):
    paymentOptionDetailType: str
    connectWallet: Optional[WalletPaymentOptionDetail]=None

class AlipayConsultPaymentResponseDTO (BaseResponseDTO):
    paymentOptions:List[PaymentOption]

class AlipayUserInitiatedPayResponseDTO (BaseResponseDTO):
    codeType: Optional[str]=None
    paymentRequestId:Optional[str]=None
    order: Optional[OrderDTO]
    customerId: Optional[str]=None
    paymentFactor: Optional[PaymentFactorDTO]=None
    paymentAmount:Optional[AmountDTO]=None
    paymentNotifyUrl: str
    paymentRedirectUrl: Optional[str]=None
    paymentExpiryTime: Optional[str]=None
    settlementStrategy: Optional[SettlementStrategyDTO]=None
    splitSettlementId: Optional[str]=None
