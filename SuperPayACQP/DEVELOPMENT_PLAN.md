# SuperPayACQP Django Application Development Plan

## Overview

This document outlines the development plan for building the SuperPayACQP system as a Django application. The system integrates with Alipay+ payment network to support payment processing, cancellation, refund, inquiry, and notification workflows.

---

## Project Structure

```
SuperPayACQP/
├── superpayacqp/                 # Project configuration
│   ├── __init__.py
│   ├── settings.py               # Django settings
│   ├── urls.py                   # Root URL configuration
│   ├── wsgi.py                   # WSGI application
│   └── asgi.py                   # ASGI application
├── apps/
│   ├── users/                    # User management
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   └── migrations/
│   ├── merchants/                # Merchant management
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   └── migrations/
│   ├── orders/                   # Order management
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   └── migrations/
│   ├── payments/                 # Payment processing
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── services.py           # Business logic
│   │   └── migrations/
│   ├── refunds/                  # Refund management
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   └── migrations/
│   └── api_records/              # API logging
│       ├── __init__.py
│       ├── models.py
│       └── migrations/
├── dtos/                         # Data Transfer Objects
│   ├── __init__.py
│   ├── base.py                   # Base DTO classes
│   ├── request/                  # Request DTOs
│   │   ├── __init__.py
│   │   ├── place_order_request.py
│   │   ├── cancel_payment_request.py
│   │   ├── refund_request.py
│   │   └── inquiry_payment_request.py
│   └── response/                 # Response DTOs
│       ├── __init__.py
│       ├── payment_response.py
│       ├── cancel_payment_response.py
│       ├── refund_response.py
│       ├── inquiry_payment_response.py
│       └── notify_payment_response.py
├── services/                     # External service integrations
│   ├── __init__.py
│   ├── alipay_client.py          # Alipay+ API client
│   └── signature_service.py      # RSA signature handling
├── middleware/                   # Custom middleware
│   ├── __init__.py
│   └── merchant_auth.py          # Merchant authentication
├── utils/                        # Utility functions
│   ├── __init__.py
│   ├── constants.py              # Constants and enums
│   ├── exceptions.py             # Custom exceptions
│   └── helpers.py                # Helper functions
├── config/                       # Configuration files
│   ├── __init__.py
│   └── settings.py               # Environment-specific settings
├── tests/                        # Test files
│   ├── __init__.py
│   ├── test_payments.py
│   ├── test_refunds.py
│   └── test_signature.py
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## Development Phases

### Phase 1: Project Setup & Infrastructure (Days 1-2)

#### 1.1 Project Initialization
- [ ] Create Django project structure
- [ ] Configure H2 database connection (using Django-H2 or similar)
- [ ] Set up environment variables management (python-dotenv)
- [ ] Configure Django REST Framework
- [ ] Set up CORS configuration

#### 1.2 Dependencies Installation
```
# requirements.txt
Django>=4.2
djangorestframework>=3.14
django-cors-headers>=4.3
python-dotenv>=1.0
requests>=2.31
cryptography>=41.0
django-filter>=23.0
drf-spectacular>=0.27  # API documentation
pydantic>=2.0          # DTO validation
pytest>=7.4
pytest-django>=4.7
```

#### 1.3 Configuration Files
- [ ] Create `.env.example` with required environment variables
- [ ] Configure logging settings
- [ ] Set up Django settings for different environments

---

### Phase 2: Database Models (Days 3-5)

#### 2.1 Users App
```python
# apps/users/models.py
from django.db import models

class User(models.Model):
    userId = models.TextField(primary_key=True)
    name = models.TextField()
    email = models.TextField(unique=True)
    password = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
```

#### 2.2 Merchants App
```python
# apps/merchants/models.py
from django.db import models

class Merchant(models.Model):
    merchantId = models.TextField(primary_key=True)
    referenceMerchantId = models.TextField(blank=True)
    merchantName = models.TextField()
    merchantDisplayName = models.TextField()
    merchantRegisterDate = models.DateTimeField(null=True, blank=True)
    merchantMCC = models.TextField(blank=True)
    merchantAddress = models.JSONField(null=True, blank=True)
    store = models.JSONField(null=True, blank=True)
    registrationDetailLegalName = models.TextField(blank=True)
    registrationDetailRegistrationType = models.TextField(blank=True)
    registrationDetailRegistrationNo = models.TextField(blank=True)
    registrationDetailRegistrationAddress = models.JSONField(null=True, blank=True)
    registrationDetailBusinessType = models.TextField(blank=True)
    websites = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'merchants'
```

#### 2.3 Orders App
```python
# apps/orders/models.py
from django.db import models

class Order(models.Model):
    orderId = models.TextField(primary_key=True)
    referenceOrderId = models.TextField(blank=True)
    orderDescription = models.TextField(blank=True)
    orderAmountValue = models.IntegerField()
    orderAmountCurrency = models.TextField()
    merchantId = models.TextField()  # FK to Merchant
    shippingName = models.JSONField(null=True, blank=True)
    shippingPhoneNo = models.TextField(blank=True)
    shippingAddress = models.JSONField(null=True, blank=True)
    shippingCarrier = models.TextField(blank=True)
    referenceBuyerId = models.TextField(blank=True)
    buyerName = models.JSONField(null=True, blank=True)
    buyerPhoneNo = models.TextField(blank=True)
    buyerEmail = models.TextField(blank=True)
    env = models.JSONField(null=True, blank=True)
    indirectAcquirer = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'


class OrderGoods(models.Model):
    id = models.AutoField(primary_key=True)
    orderId = models.TextField()  # FK to Order
    referenceGoodsId = models.TextField(blank=True)
    goodsName = models.TextField(blank=True)
    goodsCategory = models.TextField(blank=True)
    goodsBrand = models.TextField(blank=True)
    goodsUnitAmountValue = models.IntegerField()
    goodsUnitAmountCurrency = models.TextField()
    goodsQuantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order_goods'
```

#### 2.4 Payments App
```python
# apps/payments/models.py
from django.db import models

class PaymentRequest(models.Model):
    paymentRequestId = models.TextField(primary_key=True)
    acquirerId = models.TextField(blank=True)
    paymentAmountValue = models.IntegerField()
    paymentAmountCurrency = models.TextField()
    paymentMethodType = models.TextField(blank=True)
    paymentMethodId = models.TextField(blank=True)
    customerId = models.TextField(blank=True)
    paymentMethodMetaData = models.JSONField(null=True, blank=True)
    isInStorePayment = models.BooleanField(default=False)
    isCashierPayment = models.BooleanField(default=False)
    inStorePaymentScenario = models.TextField(blank=True)
    paymentExpiryTime = models.DateTimeField(null=True, blank=True)
    paymentNotifyUrl = models.TextField(blank=True)
    paymentRedirectUrl = models.TextField(blank=True)
    splitSettlementId = models.TextField(blank=True)
    settlementStrategy = models.JSONField(null=True, blank=True)
    paymentId = models.TextField(blank=True)
    paymentTime = models.DateTimeField(null=True, blank=True)
    pspId = models.TextField(blank=True)
    walletBrandName = models.TextField(blank=True)
    mppPaymentId = models.TextField(blank=True)
    customsDeclarationAmountValue = models.IntegerField(null=True)
    customsDeclarationAmountCurrency = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_requests'


class PaymentRequestResult(models.Model):
    id = models.AutoField(primary_key=True)
    paymentRequestId = models.TextField()  # FK to PaymentRequest
    isFinalStatus = models.BooleanField(default=False)
    resultStatus = models.TextField()
    resultCode = models.TextField()
    resultMessage = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_requests_result'


class Settlement(models.Model):
    settlementId = models.TextField(primary_key=True)
    paymentRequestId = models.TextField()  # FK to PaymentRequest
    settlementAmount = models.IntegerField()
    settlementCurrency = models.TextField()
    quoteId = models.TextField(blank=True)
    quotePrice = models.DecimalField(max_digits=20, decimal_places=10, null=True)
    quoteCurrencyPair = models.TextField(blank=True)
    quoteStartTime = models.DateTimeField(null=True, blank=True)
    quoteExpiryTime = models.DateTimeField(null=True, blank=True)
    quoteUnit = models.TextField(blank=True)
    baseCurrency = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'settlements'
```

#### 2.5 Refunds App
```python
# apps/refunds/models.py
from django.db import models

class RefundRecord(models.Model):
    refundRequestId = models.TextField(primary_key=True)
    paymentRequestId = models.TextField()  # FK to PaymentRequest
    paymentId = models.TextField(blank=True)
    refundAmountValue = models.IntegerField()
    refundAmountCurrency = models.TextField()
    refundReason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'refund_records'
```

#### 2.6 API Records App
```python
# apps/api_records/models.py
from django.db import models

class ApiRecord(models.Model):
    id = models.AutoField(primary_key=True)
    api_url = models.TextField()
    request_body = models.TextField()
    response_body = models.TextField()
    message_type = models.TextField()  # INBOUND or OUTBOUND
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_records'
```

---

### Phase 3: DTO Implementation (Days 6-8)

#### 3.1 Base DTO Classes
```python
# dtos/base.py
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from enum import Enum


class ResultStatus(str, Enum):
    SUCCESS = 'S'
    FAILURE = 'F'
    UNKNOWN = 'U'


class ResultDTO(BaseModel):
    resultCode: str
    resultStatus: str
    resultMessage: Optional[str] = None


class AmountDTO(BaseModel):
    currency: str
    value: int


class BaseRequestDTO(BaseModel):
    """Base class for all request DTOs"""
    
    class Config:
        extra = 'forbid'  # Reject extra fields


class BaseResponseDTO(BaseModel):
    """Base class for all response DTOs"""
    result: ResultDTO
    
    class Config:
        extra = 'allow'  # Allow extra fields in responses
```

#### 3.2 Request DTOs

##### Place Order Request DTO
```python
# dtos/request/place_order_request.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from dtos.base import BaseRequestDTO, AmountDTO


class PaymentFactorDTO(BaseModel):
    isInStorePayment: Optional[bool] = False
    isCashierPayment: Optional[bool] = False
    inStorePaymentScenario: Optional[str] = None


class NameDTO(BaseModel):
    middleName: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    fullName: Optional[str] = None


class AddressDTO(BaseModel):
    region: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    zipCode: Optional[str] = None


class ShippingDTO(BaseModel):
    shippingName: Optional[NameDTO] = None
    shippingPhoneNo: Optional[str] = None
    shippingAddress: Optional[AddressDTO] = None
    shippingCarrier: Optional[str] = None


class BuyerDTO(BaseModel):
    referenceBuyerId: Optional[str] = None
    buyerName: Optional[NameDTO] = None
    buyerPhoneNo: Optional[str] = None
    buyerEmail: Optional[str] = None


class EnvDTO(BaseModel):
    terminalType: Optional[str] = None
    osType: Optional[str] = None
    deviceTokenId: Optional[str] = None
    cookieId: Optional[str] = None
    clientIp: Optional[str] = None
    userAgent: Optional[str] = None
    storeTerminalId: Optional[str] = None
    storeTerminalRequestTime: Optional[str] = None


class GoodsDTO(BaseModel):
    referenceGoodsId: Optional[str] = None
    goodsName: Optional[str] = None
    goodsCategory: Optional[str] = None
    goodsBrand: Optional[str] = None
    goodsUnitAmount: Optional[AmountDTO] = None
    goodsQuantity: Optional[int] = None


class OrderDTO(BaseModel):
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
    order: OrderDTO
```

##### Cancel Payment Request DTO
```python
# dtos/request/cancel_payment_request.py
from pydantic import BaseModel, Field
from typing import Optional
from dtos.base import BaseRequestDTO


class CancelPaymentRequestDTO(BaseRequestDTO):
    paymentId: str
    paymentRequestId: str
```

##### Refund Request DTO
```python
# dtos/request/refund_request.py
from pydantic import BaseModel, Field
from typing import Optional
from dtos.base import BaseRequestDTO, AmountDTO


class RefundRequestDTO(BaseRequestDTO):
    paymentRequestId: str
    paymentId: str
    refundRequestId: str
    refundAmount: AmountDTO
    refundReason: Optional[str] = None
```

##### Inquiry Payment Request DTO
```python
# dtos/request/inquiry_payment_request.py
from pydantic import BaseModel, Field
from typing import Optional
from dtos.base import BaseRequestDTO


class InquiryPaymentRequestDTO(BaseRequestDTO):
    paymentId: Optional[str] = None
    paymentRequestId: str
```

#### 3.3 Response DTOs

##### Payment Response DTO
```python
# dtos/response/payment_response.py
from pydantic import BaseModel, Field
from typing import Optional
from dtos.base import BaseResponseDTO, ResultDTO, AmountDTO


class SettlementQuoteDTO(BaseModel):
    quoteId: Optional[str] = None
    quoteCurrencyPair: Optional[str] = None
    quotePrice: Optional[float] = None
    quoteStartTime: Optional[str] = None
    quoteExpiryTime: Optional[str] = None
    quoteUnit: Optional[str] = None
    baseCurrency: Optional[str] = None


class PaymentResponseDTO(BaseResponseDTO):
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
```

##### Cancel Payment Response DTO
```python
# dtos/response/cancel_payment_response.py
from pydantic import BaseModel, Field
from typing import Optional
from dtos.base import BaseResponseDTO


class CancelPaymentResponseDTO(BaseResponseDTO):
    pspId: Optional[str] = None
    acquirerId: Optional[str] = None
```

##### Refund Response DTO
```python
# dtos/response/refund_response.py
from pydantic import BaseModel, Field
from typing import Optional
from dtos.base import BaseResponseDTO, AmountDTO


class RefundResponseDTO(BaseResponseDTO):
    acquirerId: Optional[str] = None
    pspId: Optional[str] = None
    refundId: Optional[str] = None
    refundTime: Optional[str] = None
    refundAmount: Optional[AmountDTO] = None
    settlementAmount: Optional[AmountDTO] = None
    settlementQuote: Optional[dict] = None
```

##### Inquiry Payment Response DTO
```python
# dtos/response/inquiry_payment_response.py
from pydantic import BaseModel, Field
from typing import Optional, List
from dtos.base import BaseResponseDTO, ResultDTO, AmountDTO


class TransactionResultDTO(BaseModel):
    resultCode: Optional[str] = None
    resultStatus: Optional[str] = None
    resultMessage: Optional[str] = None


class TransactionDTO(BaseModel):
    transactionResult: Optional[TransactionResultDTO] = None
    transactionId: Optional[str] = None
    transactionRequestId: Optional[str] = None
    transactionAmount: Optional[AmountDTO] = None
    transactionTime: Optional[str] = None
    transactionType: Optional[str] = None
    transactionStatus: Optional[str] = None


class InquiryPaymentResponseDTO(BaseResponseDTO):
    paymentResult: Optional[ResultDTO] = None
    acquirerId: Optional[str] = None
    pspId: Optional[str] = None
    paymentRequestId: Optional[str] = None
    paymentId: Optional[str] = None
    paymentAmount: Optional[AmountDTO] = None
    paymentTime: Optional[str] = None
    customerId: Optional[str] = None
    walletBrandName: Optional[str] = None
    settlementAmount: Optional[AmountDTO] = None
    settlementQuote: Optional[dict] = None
    customsDeclarationAmount: Optional[AmountDTO] = None
    mppPaymentId: Optional[str] = None
    transactions: Optional[List[TransactionDTO]] = None
```

##### Notify Payment Response DTO
```python
# dtos/response/notify_payment_response.py
from dtos.base import BaseResponseDTO


class NotifyPaymentResponseDTO(BaseResponseDTO):
    pass  # Only contains result field
```

#### 3.4 Alipay+ Request DTOs
```python
# dtos/request/alipay_request.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from dtos.base import BaseRequestDTO, AmountDTO


class PaymentMethodDTO(BaseModel):
    paymentMethodType: str = "CONNECT_WALLET"
    paymentMethodId: Optional[str] = None
    customerId: Optional[str] = None
    paymentMethodMetaData: Optional[dict] = None


class SettlementStrategyDTO(BaseModel):
    settlementCurrency: Optional[str] = None


class StoreDTO(BaseModel):
    referenceStoreId: Optional[str] = None
    storeName: Optional[str] = None
    storeMCC: Optional[str] = None
    storeDisplayName: Optional[str] = None
    storeTerminalId: Optional[str] = None
    storeOperatorId: Optional[str] = None
    storePhoneNo: Optional[str] = None
    storeAddress: Optional[dict] = None


class MerchantInfoDTO(BaseModel):
    referenceMerchantId: Optional[str] = None
    merchantName: Optional[str] = None
    merchantDisplayName: Optional[str] = None
    merchantRegisterDate: Optional[str] = None
    merchantMCC: Optional[str] = None
    merchantAddress: Optional[dict] = None
    store: Optional[StoreDTO] = None


class IndirectAcquirerDTO(BaseModel):
    referenceAcquirerId: Optional[str] = None
    acquirerName: Optional[str] = None
    acquirerAddress: Optional[dict] = None


class AlipayOrderDTO(BaseModel):
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
```

---

### Phase 4: Security & Signature Service (Days 9-11)

#### 4.1 Signature Service Implementation
```python
# services/signature_service.py
import base64
from urllib.parse import quote, unquote
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend


class SignatureService:
    """
    Handles RSA-SHA256 signature generation and verification for Alipay+ API
    """
    
    def __init__(self, private_key: str, public_key: str, client_id: str):
        self.private_key = self._load_private_key(private_key)
        self.public_key = self._load_public_key(public_key)
        self.client_id = client_id
    
    def _load_private_key(self, key_str: str):
        """Load PKCS#8 private key from Base64 string"""
        key_bytes = base64.b64decode(key_str)
        return serialization.load_der_private_key(key_bytes, password=None, backend=default_backend())
    
    def _load_public_key(self, key_str: str):
        """Load X.509 public key from Base64 string"""
        key_bytes = base64.b64decode(key_str)
        return serialization.load_der_public_key(key_bytes, backend=default_backend())
    
    def generate_signature(self, http_method: str, request_uri: str, 
                          request_time: str, request_body: str) -> str:
        """Generate signature for request"""
        content = f"{http_method.upper()} {request_uri}\n{self.client_id}.{request_time}.{request_body or ''}"
        
        signature = self.private_key.sign(
            content.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        
        return quote(base64.b64encode(signature).decode('utf-8'))
    
    def verify_signature(self, http_method: str, request_uri: str,
                        request_time: str, request_body: str, signature: str) -> bool:
        """Verify signature from response"""
        try:
            content = f"{http_method.upper()} {request_uri}\n{self.client_id}.{request_time}.{request_body or ''}"
            
            signature_bytes = base64.b64decode(unquote(signature))
            
            self.public_key.verify(
                signature_bytes,
                content.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
    
    def build_signature_header(self, signature: str, key_version: int = 1) -> str:
        """Build signature header value"""
        return f"algorithm=RSA256,keyVersion={key_version},signature={signature}"
    
    def extract_signature_from_header(self, header: str) -> str:
        """Extract signature value from header"""
        for part in header.split(','):
            part = part.strip()
            if part.startswith('signature='):
                return part[len('signature='):]
        return None
```

#### 4.2 Merchant Authentication Middleware
```python
# middleware/merchant_auth.py
from django.http import JsonResponse


class MerchantAuthMiddleware:
    """
    Validates Merchant-ID header for all API requests
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip authentication for health check and Alipay+ callbacks
        if request.path in ['/health', '/alipay/notifyPayment']:
            return self.get_response(request)
        
        merchant_id = request.headers.get('Merchant-ID')
        if not merchant_id:
            return JsonResponse({
                'result': {
                    'resultCode': 'MISSING_MERCHANT_ID',
                    'resultStatus': 'F',
                    'resultMessage': 'Merchant-ID header is required'
                }
            }, status=403)
        
        # Validate merchant exists
        from apps.merchants.models import Merchant
        try:
            merchant = Merchant.objects.get(merchantId=merchant_id)
            request.merchant = merchant
        except Merchant.DoesNotExist:
            return JsonResponse({
                'result': {
                    'resultCode': 'INVALID_MERCHANT',
                    'resultStatus': 'F',
                    'resultMessage': 'Invalid Merchant-ID'
                }
            }, status=403)
        
        return self.get_response(request)
```

---

### Phase 5: Alipay+ Client Service (Days 12-14)

#### 5.1 Alipay+ API Client
```python
# services/alipay_client.py
import requests
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from dtos.request.alipay_request import AlipayPayRequestDTO
from dtos.request.cancel_payment_request import CancelPaymentRequestDTO
from dtos.request.refund_request import RefundRequestDTO
from dtos.request.inquiry_payment_request import InquiryPaymentRequestDTO
from dtos.response.payment_response import PaymentResponseDTO
from dtos.response.cancel_payment_response import CancelPaymentResponseDTO
from dtos.response.refund_response import RefundResponseDTO
from dtos.response.inquiry_payment_response import InquiryPaymentResponseDTO


class AlipayClient:
    """
    Client for interacting with Alipay+ API
    """
    
    BASE_URL = "https://open-sea.alipayplus.com/aps"
    
    def __init__(self, signature_service, client_id: str):
        self.signature_service = signature_service
        self.client_id = client_id
    
    def _get_request_time(self) -> str:
        """Get current UTC timestamp in ISO format"""
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    def _build_headers(self, request_uri: str, request_time: str, request_body: str) -> Dict[str, str]:
        """Build headers with signature"""
        signature = self.signature_service.generate_signature(
            "POST", request_uri, request_time, request_body
        )
        
        return {
            "Content-Type": "application/json; charset=UTF-8",
            "Client-Id": self.client_id,
            "Request-Time": request_time,
            "Signature": self.signature_service.build_signature_header(signature)
        }
    
    def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request to Alipay+ API"""
        url = f"{self.BASE_URL}{endpoint}"
        request_time = self._get_request_time()
        request_body = json.dumps(payload, separators=(',', ':'))
        
        headers = self._build_headers(endpoint, request_time, request_body)
        
        response = requests.post(url, headers=headers, data=request_body, timeout=30)
        
        # Verify response signature
        response_signature = response.headers.get('Signature')
        response_time = response.headers.get('response-time')
        
        if response_signature and response_time:
            sig_value = self.signature_service.extract_signature_from_header(response_signature)
            self.signature_service.verify_signature(
                "POST", endpoint, response_time, response.text, sig_value
            )
        
        return response.json()
    
    def pay(self, request_dto: AlipayPayRequestDTO) -> PaymentResponseDTO:
        """Call Alipay+ Pay API"""
        payload = request_dto.to_alipay_dict()
        response_data = self._make_request("/aps/api/v1/payments/pay", payload)
        return PaymentResponseDTO(**response_data)
    
    def cancel_payment(self, request_dto: CancelPaymentRequestDTO) -> CancelPaymentResponseDTO:
        """Call Alipay+ cancelPayment API"""
        payload = request_dto.model_dump(exclude_none=True)
        response_data = self._make_request("/aps/api/v1/payments/cancelPayment", payload)
        return CancelPaymentResponseDTO(**response_data)
    
    def refund(self, request_dto: RefundRequestDTO) -> RefundResponseDTO:
        """Call Alipay+ Refund API"""
        payload = request_dto.model_dump(exclude_none=True)
        response_data = self._make_request("/aps/api/v1/payments/refund", payload)
        return RefundResponseDTO(**response_data)
    
    def inquiry_payment(self, request_dto: InquiryPaymentRequestDTO) -> InquiryPaymentResponseDTO:
        """Call Alipay+ inquiryPayment API"""
        payload = request_dto.model_dump(exclude_none=True)
        response_data = self._make_request("/aps/api/v1/payments/inquiryPayment", payload)
        return InquiryPaymentResponseDTO(**response_data)
```

#### 5.2 Retry Logic Implementation
```python
# services/retry_handler.py
import time
from typing import Callable, Any, List


class RetryHandler:
    """
    Handles retry logic for API calls with configurable intervals
    """
    
    @staticmethod
    def retry_with_intervals(func: Callable, intervals: List[int], 
                            condition_check: Callable[[Any], bool]) -> Any:
        """
        Retry function with specified intervals until condition is met or retries exhausted
        
        Args:
            func: Function to call
            intervals: List of wait times in seconds between retries
            condition_check: Function that returns True if should stop retrying
        
        Returns:
            Last response from the function
        """
        response = func()
        
        if condition_check(response):
            return response
        
        for interval in intervals:
            time.sleep(interval)
            response = func()
            
            if condition_check(response):
                return response
        
        return response
    
    @staticmethod
    def retry_until_timeout(func: Callable, interval: int, timeout: int,
                           condition_check: Callable[[Any], bool]) -> Any:
        """
        Retry function at fixed interval until timeout
        
        Args:
            func: Function to call
            interval: Wait time in seconds between retries
            timeout: Total time in seconds to retry
            condition_check: Function that returns True if should stop retrying
        
        Returns:
            Last response from the function
        """
        start_time = time.time()
        response = func()
        
        if condition_check(response):
            return response
        
        while time.time() - start_time < timeout:
            time.sleep(interval)
            response = func()
            
            if condition_check(response):
                return response
        
        return response
```

---

### Phase 6: API Views Implementation (Days 15-19)

#### 6.1 Place Order API
```python
# apps/payments/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta, timezone
import uuid
import json

from django.conf import settings
from .models import PaymentRequest, PaymentRequestResult, Settlement
from apps.api_records.models import ApiRecord
from apps.merchants.models import Merchant

from dtos.request.place_order_request import PlaceOrderRequestDTO
from dtos.request.alipay_request import AlipayPayRequestDTO, PaymentMethodDTO, AlipayOrderDTO
from dtos.request.inquiry_payment_request import InquiryPaymentRequestDTO
from dtos.response.payment_response import PaymentResponseDTO

from services.alipay_client import AlipayClient
from services.signature_service import SignatureService
from services.retry_handler import RetryHandler


class PlaceOrderView(APIView):
    """
    POST /api/place-order
    Place an order and initiate payment
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.signature_service = SignatureService(
            private_key=settings.ALIPAY_PRIVATE_KEY,
            public_key=settings.ALIPAY_PUBLIC_KEY,
            client_id=settings.ALIPAY_CLIENT_ID
        )
        self.alipay_client = AlipayClient(self.signature_service, settings.ALIPAY_CLIENT_ID)
    
    def post(self, request):
        # Parse and validate request using DTO
        try:
            request_dto = PlaceOrderRequestDTO(**request.data)
        except Exception as e:
            return Response({
                'result': {
                    'resultCode': 'INVALID_REQUEST',
                    'resultStatus': 'F',
                    'resultMessage': str(e)
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate payment request ID
        payment_request_id = str(uuid.uuid4())
        
        # Calculate expiry time (current time + 1 minute)
        expiry_time = datetime.now(timezone.utc) + timedelta(minutes=1)
        
        # Build Alipay+ request DTO
        alipay_request_dto = self._build_alipay_request_dto(
            request_dto, 
            payment_request_id, 
            expiry_time
        )
        
        # Call Alipay+ Pay API
        response_dto = self.alipay_client.pay(alipay_request_dto)
        
        # Log API record
        ApiRecord.objects.create(
            api_url='/aps/api/v1/payments/pay',
            request_body=json.dumps(alipay_request_dto.to_alipay_dict()),
            response_body=response_dto.model_dump_json(),
            message_type='OUTBOUND'
        )
        
        # Process result
        result = response_dto.result
        result_status = result.resultStatus
        result_code = result.resultCode
        
        # Handle PAYMENT_IN_PROCESS with retry
        if result_status == 'U' and result_code == 'PAYMENT_IN_PROCESS':
            response_dto = self._handle_payment_in_process(payment_request_id)
        
        # Handle UNKNOWN_EXCEPTION with retry
        elif result_status == 'U' and result_code == 'UNKNOWN_EXCEPTION':
            response_dto = self.alipay_client.pay(alipay_request_dto)
        
        # Save payment request to database
        self._save_payment_request(alipay_request_dto, response_dto, payment_request_id)
        
        return Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK)
    
    def _build_alipay_request_dto(self, request_dto: PlaceOrderRequestDTO, 
                                   payment_request_id: str, 
                                   expiry_time: datetime) -> AlipayPayRequestDTO:
        """Build Alipay+ Pay API request DTO"""
        order = request_dto.order
        
        # Get merchant info
        merchant_info = self._get_merchant_info(order.merchantId)
        
        return AlipayPayRequestDTO(
            paymentRequestId=payment_request_id,
            paymentAmount=order.orderAmount,
            paymentMethod=PaymentMethodDTO(paymentMethodType="CONNECT_WALLET"),
            paymentFactor=order.paymentFactor.model_dump(exclude_none=True) if order.paymentFactor else None,
            paymentExpiryTime=expiry_time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
            order=AlipayOrderDTO(
                referenceOrderId=order.referenceOrderId,
                orderDescription=order.orderDescription,
                orderAmount=order.orderAmount,
                merchant=merchant_info,
                goods=[g.model_dump(exclude_none=True) for g in order.goods] if order.goods else None,
                shipping=order.shipping.model_dump(exclude_none=True) if order.shipping else None,
                buyer=order.buyer.model_dump(exclude_none=True) if order.buyer else None,
                env=order.env.model_dump(exclude_none=True) if order.env else None
            )
        )
    
    def _get_merchant_info(self, merchant_id: str):
        """Get merchant info from database"""
        try:
            merchant = Merchant.objects.get(merchantId=merchant_id)
            return {
                'referenceMerchantId': merchant.referenceMerchantId,
                'merchantName': merchant.merchantName,
                'merchantDisplayName': merchant.merchantDisplayName,
                'merchantMCC': merchant.merchantMCC,
                'merchantAddress': merchant.merchantAddress
            }
        except Merchant.DoesNotExist:
            return None
    
    def _handle_payment_in_process(self, payment_request_id: str) -> PaymentResponseDTO:
        """Handle PAYMENT_IN_PROCESS with inquiry retry"""
        intervals = [2, 2, 3, 3, 5, 5, 10, 10, 10, 10]
        
        inquiry_dto = InquiryPaymentRequestDTO(paymentRequestId=payment_request_id)
        
        def inquiry():
            return self.alipay_client.inquiry_payment(inquiry_dto)
        
        def should_stop(response):
            result = response.result
            return result.resultStatus != 'U' or result.resultCode != 'UNKNOWN_EXCEPTION'
        
        return RetryHandler.retry_with_intervals(inquiry, intervals, should_stop)
    
    def _save_payment_request(self, request_dto: AlipayPayRequestDTO, 
                              response_dto: PaymentResponseDTO, 
                              payment_request_id: str):
        """Save payment request to database"""
        PaymentRequest.objects.create(
            paymentRequestId=payment_request_id,
            acquirerId=response_dto.acquirerId or '',
            paymentAmountValue=request_dto.paymentAmount.value,
            paymentAmountCurrency=request_dto.paymentAmount.currency,
            paymentMethodType=request_dto.paymentMethod.paymentMethodType,
            paymentExpiryTime=request_dto.paymentExpiryTime,
            paymentId=response_dto.paymentId or '',
            paymentTime=response_dto.paymentTime,
            pspId=response_dto.pspId or '',
            walletBrandName=response_dto.walletBrandName or '',
            mppPaymentId=response_dto.mppPaymentId or ''
        )
```

#### 6.2 Cancel Payment API
```python
# apps/payments/views.py (continued)
from dtos.request.cancel_payment_request import CancelPaymentRequestDTO
from dtos.response.cancel_payment_response import CancelPaymentResponseDTO


class CancelPaymentView(APIView):
    """
    POST /api/cancel-payment
    Cancel a payment
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.signature_service = SignatureService(
            private_key=settings.ALIPAY_PRIVATE_KEY,
            public_key=settings.ALIPAY_PUBLIC_KEY,
            client_id=settings.ALIPAY_CLIENT_ID
        )
        self.alipay_client = AlipayClient(self.signature_service, settings.ALIPAY_CLIENT_ID)
    
    def post(self, request):
        # Parse and validate request using DTO
        try:
            request_dto = CancelPaymentRequestDTO(**request.data)
        except Exception as e:
            return Response({
                'result': {
                    'resultCode': 'INVALID_REQUEST',
                    'resultStatus': 'F',
                    'resultMessage': str(e)
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Call Alipay+ cancelPayment API
        response_dto = self.alipay_client.cancel_payment(request_dto)
        
        # Log API record
        ApiRecord.objects.create(
            api_url='/aps/api/v1/payments/cancelPayment',
            request_body=request_dto.model_dump_json(),
            response_body=response_dto.model_dump_json(),
            message_type='OUTBOUND'
        )
        
        # Handle UNKNOWN_EXCEPTION with retry
        result = response_dto.result
        if result.resultStatus == 'U' and result.resultCode == 'UNKNOWN_EXCEPTION':
            response_dto = self._retry_cancel(request_dto)
        
        return Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK)
    
    def _retry_cancel(self, request_dto: CancelPaymentRequestDTO) -> CancelPaymentResponseDTO:
        """Retry cancel for UNKNOWN_EXCEPTION"""
        def cancel():
            return self.alipay_client.cancel_payment(request_dto)
        
        def should_stop(response):
            result = response.result
            return result.resultStatus != 'U' or result.resultCode != 'UNKNOWN_EXCEPTION'
        
        return RetryHandler.retry_until_timeout(cancel, 10, 60, should_stop)
```

#### 6.3 Refund API
```python
# apps/refunds/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.conf import settings
from .models import RefundRecord
from apps.api_records.models import ApiRecord

from dtos.request.refund_request import RefundRequestDTO
from dtos.response.refund_response import RefundResponseDTO
from services.alipay_client import AlipayClient
from services.signature_service import SignatureService


class RefundView(APIView):
    """
    POST /api/refund
    Initiate a refund request
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.signature_service = SignatureService(
            private_key=settings.ALIPAY_PRIVATE_KEY,
            public_key=settings.ALIPAY_PUBLIC_KEY,
            client_id=settings.ALIPAY_CLIENT_ID
        )
        self.alipay_client = AlipayClient(self.signature_service, settings.ALIPAY_CLIENT_ID)
    
    def post(self, request):
        # Parse and validate request using DTO
        try:
            request_dto = RefundRequestDTO(**request.data)
        except Exception as e:
            return Response({
                'result': {
                    'resultCode': 'INVALID_REQUEST',
                    'resultStatus': 'F',
                    'resultMessage': str(e)
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Call Alipay+ Refund API
        response_dto = self.alipay_client.refund(request_dto)
        
        # Log API record
        ApiRecord.objects.create(
            api_url='/aps/api/v1/payments/refund',
            request_body=request_dto.model_dump_json(),
            response_body=response_dto.model_dump_json(),
            message_type='OUTBOUND'
        )
        
        # Save refund record if successful
        result = response_dto.result
        if result.resultStatus == 'S':
            RefundRecord.objects.create(
                refundRequestId=request_dto.refundRequestId,
                paymentRequestId=request_dto.paymentRequestId,
                paymentId=request_dto.paymentId,
                refundAmountValue=request_dto.refundAmount.value,
                refundAmountCurrency=request_dto.refundAmount.currency,
                refundReason=request_dto.refundReason or ''
            )
        
        return Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK)
```

#### 6.4 Inquiry Payment API
```python
# apps/payments/views.py (continued)
from dtos.request.inquiry_payment_request import InquiryPaymentRequestDTO
from dtos.response.inquiry_payment_response import InquiryPaymentResponseDTO


class InquiryPaymentView(APIView):
    """
    POST /api/inquiryPayment
    Query payment result
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.signature_service = SignatureService(
            private_key=settings.ALIPAY_PRIVATE_KEY,
            public_key=settings.ALIPAY_PUBLIC_KEY,
            client_id=settings.ALIPAY_CLIENT_ID
        )
        self.alipay_client = AlipayClient(self.signature_service, settings.ALIPAY_CLIENT_ID)
    
    def post(self, request):
        # Parse and validate request using DTO
        try:
            request_dto = InquiryPaymentRequestDTO(**request.data)
        except Exception as e:
            return Response({
                'result': {
                    'resultCode': 'INVALID_REQUEST',
                    'resultStatus': 'F',
                    'resultMessage': str(e)
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Call Alipay+ inquiryPayment API
        response_dto = self.alipay_client.inquiry_payment(request_dto)
        
        # Log API record
        ApiRecord.objects.create(
            api_url='/aps/api/v1/payments/inquiryPayment',
            request_body=request_dto.model_dump_json(),
            response_body=response_dto.model_dump_json(),
            message_type='OUTBOUND'
        )
        
        # Handle UNKNOWN_EXCEPTION with retry
        result = response_dto.result
        if result.resultStatus == 'U' and result.resultCode == 'UNKNOWN_EXCEPTION':
            response_dto = self._handle_inquiry_retry(request_dto)
        
        return Response(response_dto.model_dump(exclude_none=True), status=status.HTTP_200_OK)
    
    def _handle_inquiry_retry(self, request_dto: InquiryPaymentRequestDTO) -> InquiryPaymentResponseDTO:
        """Handle inquiry retry with automatic cancel on expiry"""
        # Get payment request to check expiry time
        try:
            payment_request = PaymentRequest.objects.get(paymentRequestId=request_dto.paymentRequestId)
            expiry_time = payment_request.paymentExpiryTime
        except PaymentRequest.DoesNotExist:
            expiry_time = datetime.now(timezone.utc) + timedelta(minutes=1)
        
        def inquiry():
            return self.alipay_client.inquiry_payment(request_dto)
        
        def should_stop(response):
            result = response.result
            if result.resultStatus != 'U':
                return True
            # Check if expired
            if datetime.now(timezone.utc) > expiry_time:
                return True
            return False
        
        response_dto = RetryHandler.retry_until_timeout(inquiry, 5, 60, should_stop)
        
        # If still unknown after expiry, trigger cancel
        result = response_dto.result
        if result.resultStatus == 'U' and datetime.now(timezone.utc) > expiry_time:
            cancel_dto = CancelPaymentRequestDTO(
                paymentId=request_dto.paymentId,
                paymentRequestId=request_dto.paymentRequestId
            )
            cancel_response = self.alipay_client.cancel_payment(cancel_dto)
            ApiRecord.objects.create(
                api_url='/aps/api/v1/payments/cancelPayment',
                request_body=cancel_dto.model_dump_json(),
                response_body=cancel_response.model_dump_json(),
                message_type='OUTBOUND'
            )
        
        return response_dto
```

#### 6.5 Notify Payment Callback
```python
# apps/payments/views.py (continued)
from dtos.response.notify_payment_response import NotifyPaymentResponseDTO


class NotifyPaymentView(APIView):
    """
    POST /alipay/notifyPayment
    Receive payment notification from Alipay+
    """
    authentication_classes = []  # No authentication for Alipay+ callback
    permission_classes = []
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.signature_service = SignatureService(
            private_key=settings.ALIPAY_PRIVATE_KEY,
            public_key=settings.ALIPAY_PUBLIC_KEY,
            client_id=settings.ALIPAY_CLIENT_ID
        )
    
    def post(self, request):
        # Verify signature
        signature_header = request.headers.get('Signature', '')
        request_time = request.headers.get('Request-Time', '')
        
        signature = self.signature_service.extract_signature_from_header(signature_header)
        
        is_valid = self.signature_service.verify_signature(
            'POST',
            '/alipay/notifyPayment',
            request_time,
            request.body.decode('utf-8'),
            signature
        )
        
        if not is_valid:
            response_dto = NotifyPaymentResponseDTO(
                result={
                    'resultCode': 'INVALID_SIGNATURE',
                    'resultStatus': 'F',
                    'resultMessage': 'Signature verification failed'
                }
            )
            return Response(response_dto.model_dump(), status=status.HTTP_200_OK)
        
        # Log API record
        ApiRecord.objects.create(
            api_url='/alipay/notifyPayment',
            request_body=request.body.decode('utf-8'),
            response_body='',
            message_type='INBOUND'
        )
        
        # Process notification
        notification_data = request.data
        payment_request_id = notification_data.get('paymentRequestId')
        
        # Update payment request
        try:
            payment_request = PaymentRequest.objects.get(paymentRequestId=payment_request_id)
            payment_request.paymentId = notification_data.get('paymentId', '')
            payment_request.paymentTime = notification_data.get('paymentTime')
            payment_request.pspId = notification_data.get('pspId', '')
            payment_request.walletBrandName = notification_data.get('walletBrandName', '')
            payment_request.mppPaymentId = notification_data.get('mppPaymentId', '')
            payment_request.save()
            
            # Save payment result
            payment_result = notification_data.get('paymentResult', {})
            PaymentRequestResult.objects.create(
                paymentRequestId=payment_request_id,
                isFinalStatus=True,
                resultStatus=payment_result.get('resultStatus', ''),
                resultCode=payment_result.get('resultCode', ''),
                resultMessage=payment_result.get('resultMessage', '')
            )
            
            # Save settlement if present
            settlement_amount = notification_data.get('settlementAmount', {})
            settlement_quote = notification_data.get('settlementQuote', {})
            
            if settlement_amount:
                Settlement.objects.create(
                    settlementId=str(uuid.uuid4()),
                    paymentRequestId=payment_request_id,
                    settlementAmount=settlement_amount.get('value', 0),
                    settlementCurrency=settlement_amount.get('currency', ''),
                    quoteId=settlement_quote.get('quoteId', ''),
                    quotePrice=settlement_quote.get('quotePrice'),
                    quoteCurrencyPair=settlement_quote.get('quoteCurrencyPair', ''),
                    quoteStartTime=settlement_quote.get('quoteStartTime'),
                    quoteExpiryTime=settlement_quote.get('quoteExpiryTime'),
                    quoteUnit=settlement_quote.get('quoteUnit', ''),
                    baseCurrency=settlement_quote.get('baseCurrency', '')
                )
        except PaymentRequest.DoesNotExist:
            pass  # Log warning but still return success
        
        response_dto = NotifyPaymentResponseDTO(
            result={
                'resultCode': 'SUCCESS',
                'resultStatus': 'S',
                'resultMessage': 'Notification processed successfully'
            }
        )
        return Response(response_dto.model_dump(), status=status.HTTP_200_OK)
```

---

### Phase 7: URL Configuration (Day 20)

```python
# superpayacqp/urls.py
from django.urls import path
from apps.payments.views import (
    PlaceOrderView, 
    CancelPaymentView, 
    InquiryPaymentView,
    NotifyPaymentView
)
from apps.refunds.views import RefundView

urlpatterns = [
    # SuperPayACQP Endpoints
    path('api/place-order', PlaceOrderView.as_view(), name='place-order'),
    path('api/cancel-payment', CancelPaymentView.as_view(), name='cancel-payment'),
    path('api/refund', RefundView.as_view(), name='refund'),
    path('api/inquiryPayment', InquiryPaymentView.as_view(), name='inquiry-payment'),
    
    # Alipay+ Callback
    path('alipay/notifyPayment', NotifyPaymentView.as_view(), name='notify-payment'),
]
```

---

### Phase 8: Settings Configuration (Day 21)

```python
# superpayacqp/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'your-secret-key')

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    # Local apps
    'apps.users',
    'apps.merchants',
    'apps.orders',
    'apps.payments',
    'apps.refunds',
    'apps.api_records',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'middleware.merchant_auth.MerchantAuthMiddleware',
]

ROOT_URLCONF = 'superpayacqp.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.h2',
        'NAME': os.getenv('DB_NAME', 'superpayacqp'),
        'USER': os.getenv('DB_USER', 'sa'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', ''),
        'PORT': os.getenv('DB_PORT', ''),
    }
}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'utils.exceptions.custom_exception_handler',
}

# Alipay+ Configuration
ALIPAY_PUBLIC_KEY = os.getenv('ALIPAY_PUBLIC_KEY', '')
ALIPAY_PRIVATE_KEY = os.getenv('ALIPAY_PRIVATE_KEY', '')
ALIPAY_CLIENT_ID = os.getenv('ALIPAY_CLIENT_ID', '')

# CORS Configuration
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000').split(',')

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/superpayacqp.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
        'services': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
    },
}
```

---

### Phase 9: Testing (Days 22-24)

#### 9.1 Unit Tests
```python
# tests/test_signature.py
import pytest
from django.conf import settings
from services.signature_service import SignatureService


class TestSignatureService:
    
    @pytest.fixture
    def signature_service(self):
        return SignatureService(
            private_key=settings.ALIPAY_PRIVATE_KEY,
            public_key=settings.ALIPAY_PUBLIC_KEY,
            client_id=settings.ALIPAY_CLIENT_ID
        )
    
    def test_generate_and_verify_signature(self, signature_service):
        """Test signature generation and verification"""
        http_method = "POST"
        request_uri = "/aps/api/v1/payments/pay"
        request_time = "2024-01-15T10:30:00Z"
        request_body = '{"paymentRequestId":"test-123"}'
        
        # Generate signature
        signature = signature_service.generate_signature(
            http_method, request_uri, request_time, request_body
        )
        
        assert signature is not None
        assert len(signature) > 0
        
        # Verify signature
        is_valid = signature_service.verify_signature(
            http_method, request_uri, request_time, request_body, signature
        )
        
        assert is_valid is True
    
    def test_verify_invalid_signature(self, signature_service):
        """Test verification with invalid signature"""
        is_valid = signature_service.verify_signature(
            "POST", "/test", "2024-01-15T10:30:00Z", "{}", "invalid_signature"
        )
        
        assert is_valid is False
```

#### 9.2 DTO Tests
```python
# tests/test_dtos.py
import pytest
from dtos.request.place_order_request import PlaceOrderRequestDTO, OrderDTO
from dtos.base import AmountDTO


class TestPlaceOrderRequestDTO:
    
    def test_valid_request(self):
        """Test valid place order request"""
        data = {
            "order": {
                "referenceOrderId": "order-123",
                "orderDescription": "Test order",
                "orderAmount": {
                    "currency": "MYR",
                    "value": 1000
                },
                "merchantId": "merchant-001"
            }
        }
        
        dto = PlaceOrderRequestDTO(**data)
        
        assert dto.order.referenceOrderId == "order-123"
        assert dto.order.orderAmount.currency == "MYR"
        assert dto.order.orderAmount.value == 1000
        assert dto.order.merchantId == "merchant-001"
    
    def test_missing_required_field(self):
        """Test request with missing required field"""
        data = {
            "order": {
                "referenceOrderId": "order-123"
            }
        }
        
        with pytest.raises(Exception):  # ValidationError
            PlaceOrderRequestDTO(**data)
    
    def test_extra_field_rejected(self):
        """Test that extra fields are rejected"""
        data = {
            "order": {
                "referenceOrderId": "order-123",
                "orderAmount": {
                    "currency": "MYR",
                    "value": 1000
                },
                "merchantId": "merchant-001"
            },
            "extraField": "should be rejected"
        }
        
        with pytest.raises(Exception):  # ValidationError
            PlaceOrderRequestDTO(**data)
```

#### 9.3 Integration Tests
```python
# tests/test_payments.py
import pytest
from django.test import RequestFactory
from apps.payments.views import PlaceOrderView


class TestPlaceOrderAPI:
    
    @pytest.fixture
    def factory(self):
        return RequestFactory()
    
    def test_place_order_missing_merchant_id(self, factory):
        """Test place order without Merchant-ID header"""
        request = factory.post(
            '/api/place-order',
            data={},
            content_type='application/json'
        )
        
        view = PlaceOrderView.as_view()
        response = view(request)
        
        assert response.status_code == 403
    
    def test_place_order_invalid_request(self, factory):
        """Test place order with invalid request body"""
        request = factory.post(
            '/api/place-order',
            data={},
            content_type='application/json',
            HTTP_MERCHANT_ID='test-merchant'
        )
        
        view = PlaceOrderView.as_view()
        response = view(request)
        
        assert response.status_code == 400
```

---

### Phase 10: Documentation & Deployment (Days 25-27)

#### 10.1 API Documentation
- [ ] Configure drf-spectacular for OpenAPI documentation
- [ ] Add API endpoint descriptions
- [ ] Generate Swagger UI

#### 10.2 Deployment Preparation
- [ ] Create Dockerfile
- [ ] Create docker-compose.yml
- [ ] Configure production settings
- [ ] Set up logging and monitoring

#### 10.3 README Documentation
- [ ] Project overview
- [ ] Installation instructions
- [ ] Configuration guide
- [ ] API usage examples

---

## Environment Variables

```bash
# .env.example

# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=superpayacqp
DB_USER=sa
DB_PASSWORD=
DB_HOST=
DB_PORT=

# Alipay+ Configuration
ALIPAY_PUBLIC_KEY=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAtXbe4yU4x1XbpXcwNfynVgo4+RHc/vhV90ImyAqLabvXQlS5/JQQ+gKaO3R5qqu9E0AlWTL/uzFKnlxqkAwjePD9UC1UEkgWqxsM+ZzEuZF1Urd7klHBt4VUItHocoPJinFkIDX+EnbkObCXq80aPUg438ouGXE8c18rlmBmUk+08Y3VrH/O0+yxPXOkbA0El1B/ILZlCrgMKUx6cqwv5XX7YgCSGxwEtuLGFeGZnJHPcfOo6hJoGdXuE0Wi0vO5lwobxszMcAyq6Rkf+AzoR0ziE+5kvsqowl6WP7rqSPuOYPqxvl4u4eqU+qkWAzSwqxPnTa1zHyhAqraUwM3AaQIDAQAB
ALIPAY_PRIVATE_KEY=MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCKkMvH8hBhjOWJRAQPNBIqKgXfvYm4LYEjlUoPZtmTt4NFY/llfd6wNlHM5KpmZB4oTsyDgmvnZqzm0yZ4D4YMFlJe2ziuX9BKRTXXLniKJ+gXM5BflFLHMxlx2UzspKIlQ5guafULqtATAaHBlTdOLTuSJDlxM/Iu0zvaRftz9cY2zR1Nf5Yd7Nghw4B4zxtfgM2x1pnHN/H/tHvaVNCMk4NkYb+1ZyNjxMQ4jnMcXtLgIWzzNUTiw1+CnH00j4uyN5zdiD6EkMUGEQ0njPegZuxnCfUkq1ljP53dJqh5kNU9ih+Piv3LbUweqaZe6vk8bqvnX3DhOlWfkBIc6a9HAgMBAAECggEBAIWvjzv3+f/zzNzzJyt35HKTmpkzp3RvSqGG/i3/37kZm2fOPabCmp/NuHwCvbgNrd7br4rNwMc/k18bpoi9CWoN+yiTPotV24JcZcaWiitYtx3zXL4qPvb7APiLWyEQ8XMcVO2qwoWgJiHAOEypZvNgxpGHq3fhUy4EFEHRtPk5YEYHAdrSXG0Cd12DiV4OVgHweJMD8qEmWzA6UYGTzojYEC0hUwmg4bZgjLbkxGoQQdFs9AnEn11K6gi/EmQQyaQCuaGF26kUWUhA7HDNc7foZy/dIzi4QCNj+e9EeKgcmMaLLZTu/bRDlvpCY19se4OaiJcILNxneYmUfnACQ9ECgYEAzeSK8rJ2Ovd3MtOLqNmvMy6pJa9TLlCQD/5x5wJ8MGygRGwji54q6C/T9LdKbMdg9wXmC4XyQFI/O4ywJgTOb10SYh1LcKLlzJP0GogfY1gVTqxCzntFaQBBxOVWGyIf0aP0IjRtBsWGDmeGEwhDT0e59hWY8OugWGTyJnW6Nj8CgYEArEmpaisDoEPvYPRGZenTY5FoZd33jV8g4AO9bB3v9D5ao7PTIxHlMHbpD5M0MmMtAuVmP0OtnhQF95h08Q9HRJ1bn0fwNnpSpR6ZIQPF+FBqdoxsFOJVjujqoG4QylBSm7QpiN02yhjJG+7aST4cohzxQ09Hv9OTAmMLNHnyFPkCgYEAngVJK0oS+eDSSF0aNEaWc8bdJUIxqjtExjG4Q9+hZx0HyFvi0BZdwgRrPcerRF+lqRGK5M8yBXHafB7XVuabdddN86WeL92mV2Q6ll5hEMMa313QjF8J/7OlxrNpabvABgs6pUHtZ6QT5lxIB7Vwy5k2PYuH7Wg6kX0waJo0h8sCgYBDywh62kom+hRrljNNTuD7QPBPhTQv0Mri2xXiQTV2akLIP65JEnWYyHGUy1uyqAvCI/pD0qGynjZq4vbBFD365eBzoJ8JEMEMcCnZL97qgtoho8ezwAvinAwW7Lh2o3yeABqH3GP+yhn4f9gtEd+6eqEE12FoPhyOx+JU19dGIQKBgEP4yFkcp0nsUGLgDw+trLPmgx98rLRFHtyuOdpwFF7G3gqJpdFUaaLEEx+HpQvsGL4SY3luT2WGKpNa/+78jm6BBkmKodEVyeXaA7g+HQHFFcam5Zjzix9vqKNd+iOXsmf4psHzC1n8Xo/KnSz/PVC6OZ89YnRml6QcpK4x3+4C
ALIPAY_CLIENT_ID=SANDBOX_5YHQ7N30CPL702872

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

---

## Timeline Summary

| Phase | Description | Duration |
|-------|-------------|----------|
| 1 | Project Setup & Infrastructure | 2 days |
| 2 | Database Models | 3 days |
| 3 | DTO Implementation | 3 days |
| 4 | Security & Signature Service | 3 days |
| 5 | Alipay+ Client Service | 3 days |
| 6 | API Views Implementation | 5 days |
| 7 | URL Configuration | 1 day |
| 8 | Settings Configuration | 1 day |
| 9 | Testing | 3 days |
| 10 | Documentation & Deployment | 3 days |
| **Total** | | **27 days** |

---

## Key Technical Decisions

1. **Database**: H2 database as specified in the design document
2. **Field Types**: All ID and string fields use `TextField` for flexibility
3. **API Framework**: Django REST Framework for building RESTful APIs
4. **DTO Pattern**: Pydantic models for request/response validation and serialization
5. **Signature**: Using `cryptography` library for RSA-SHA256 signatures
6. **Retry Logic**: Custom retry handler with configurable intervals
7. **Authentication**: Custom middleware for Merchant-ID header validation
8. **Logging**: Comprehensive logging for API records and debugging

---

## DTO Pattern Benefits

1. **Type Safety**: Pydantic provides runtime type validation
2. **Documentation**: DTOs serve as self-documenting code
3. **Validation**: Automatic validation of request data
4. **Serialization**: Easy conversion to/from JSON
5. **Maintainability**: Clear separation between API contracts and internal models
6. **Testing**: Easy to create test fixtures using DTOs

---

## Next Steps

1. Review and approve this development plan
2. Set up the development environment
3. Begin Phase 1 implementation
