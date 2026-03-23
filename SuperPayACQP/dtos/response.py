"""
Response DTOs
"""
from dtos import BaseResponseDTO, AmountDTO
from pydantic import BaseModel
from typing import Optional, List
from utils.constants import Result

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
