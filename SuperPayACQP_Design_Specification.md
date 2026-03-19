# 1. SuperPayACQP background:

SuperPayACQP is an ACQP system that integrates with an ecommerce website and also Alipay+ payment network, supporting payment processing, cancellation, refund, inquiry, and notification workflows.

# 2. Database Design:

Database: H2
Database name: superpayacqp

Table name: users

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| userId | TEXT | Primary key |
| name | TEXT | User name |
| email | TEXT | User email |
| password | TEXT | User password |
| created_at | timestamp | Creation time |
| updated_at | timestamp | Update time |

Table name: merchants

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| merchantId | TEXT | Primary key |
| referenceMerchantId | TEXT | Reference merchant ID |
| merchantName | TEXT | Merchant name |
| merchantDisplayName | TEXT | Merchant display name |
| merchantRegisterDate | timestamp | Merchant register date |
| merchantMCC | TEXT | Merchant MCC |
| merchantAddress | JSON | Merchant address |
| store | JSON | Store information |
| registrationDetailLegalName | TEXT | The merchant's legal name for business registration. |
| registrationDetailRegistrationType | TEXT | The merchant's business registration type |
| registrationDetailRegistrationNo | TEXT | The merchant's business registration number. |
| registrationDetailRegistrationAddress | JSON | The merchant's address for business registration. |
| registrationDetailBusinessType | TEXT | The business type of the merchant. |
| websites | JSON | Websites information |
| created_at | timestamp | Creation time |
| updated_at | timestamp | Update time |

Table name: payment_requests

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| paymentRequestId | TEXT | Primary key |
| acquirerId | TEXT | Acquirer ID |
| paymentAmountValue | Integer | Payment amount |
| paymentAmountCurrency | TEXT | Payment amount currency |
| paymentMethodType | TEXT | Payment method type |
| paymentMethodId | TEXT | Payment method id |
| customerId | TEXT | Customer id |
| paymentMethodMetaData | JSON | Payment method meta data |
| isInStorePayment | boolean | Payment factor-isInStorePayment |
| isCashierPayment | boolean | Payment factor-isCashierPayment |
| inStorePaymentScenario | TEXT | Payment factor-inStorePaymentScenario |
| paymentExpiryTime | timestamp | Payment expiry time |
| paymentNotifyUrl | TEXT | Payment notify url |
| paymentRedirectUrl | TEXT | Payment redirect url |
| splitSettlementId | TEXT | Split settlement id |
| settlementStrategy | JSON | Settlement strategy |
| paymentId | TEXT | Payment id |
| paymentTime | timestamp | Payment time |
| pspId | TEXT | pspId |
| walletBrandName | TEXT | walletBrandName |
| mppPaymentId | TEXT | MPP Payment id |
| customsDeclarationAmountValue | Integer | Customs declaration amount |
| customsDeclarationAmountCurrency | TEXT | Customs declaration currency |
| created_at | timestamp | Creation time |
| updated_at | timestamp | Update time |

Table name: payment_requests_result

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| id | int | Primary key |
| paymentRequestId | TEXT | Foreign key to payment_requests table |
| isFinalStatus | boolean | Is final status |
| resultStatus | TEXT | Payment status |
| resultCode | TEXT | Payment result code |
| resultMessage | TEXT | Payment result message |
| created_at | timestamp | Creation time |
| updated_at | timestamp | Update time |

Table name: settlements

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| settlementId | TEXT | Primary key |
| paymentRequestId | TEXT | Foreign key to payment_requests table |
| settlementAmount | Integer | Settlement amount |
| settlementCurrency | TEXT | Settlement currency |
| quoteId | TEXT | Quote ID |
| quotePrice | decimal | Quote price |
| quoteCurrencyPair | TEXT | Quote currency pair |
| quoteStartTime | timestamp | Quote start time |
| quoteExpiryTime | timestamp | Quote expiry time |
| quoteUnit | TEXT | Quote unit |
| baseCurrency | TEXT | Quote base currency |
| created_at | timestamp | Creation time |
| updated_at | timestamp | Update time |

Table name: orders

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| orderId | TEXT | Primary key |
| referenceOrderId | TEXT | Reference order id |
| orderDescription | TEXT | Order description |
| orderAmountValue | Integer | Order amount |
| orderAmountCurrency | TEXT | Order amount currency |
| merchantId | TEXT | Foreign key to merchants table |
| shippingName | JSON | Shipping name |
| shippingPhoneNo | TEXT | Shipping phone no |
| shippingAddress | JSON | Shipping address |
| shippingCarrier | TEXT | Shipping carrier |
| referenceBuyerId | TEXT | Reference buyer id |
| buyerName | JSON | Buyer name |
| buyerPhoneNo | TEXT | Buyer phone no |
| buyerEmail | TEXT | Buyer email address |
| env | JSON | Env |
| indirectAcquirer | JSON | Indirect acquirer |
| created_at | timestamp | Creation time |
| updated_at | timestamp | Update time |

Table name: order_goods

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| id | int | Primary key |
| orderId | TEXT | Foreign key to orders table |
| referenceGoodsId | TEXT | Reference goods id |
| goodsName | TEXT | Goods name |
| goodsCategory | TEXT | Goods category |
| goodsBrand | TEXT | Goods brand |
| goodsUnitAmountValue | Integer | Goods unit amount |
| goodsUnitAmountCurrency | TEXT | Goods unit amount currency |
| goodsQuantity | Integer | Goods quantity |
| created_at | timestamp | Creation time |
| updated_at | timestamp | Update time |

Table name: api_records

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| id | int | Primary key |
| api_url | TEXT | API url |
| request_body | TEXT | Request body |
| response_body | TEXT | Response body |
| message_type | TEXT | INBOUND or OUTBOUND |
| created_at | timestamp | Creation time |
| updated_at | timestamp | Update time |

Table name: refund_records

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| refundRequestId | TEXT | Primary key |
| paymentRequestId | TEXT | Foreign key to payment_requests table |
| paymentId | TEXT | Payment id |
| refundAmountValue | Integer | Refund amount |
| refundAmountCurrency | TEXT | Refund currency |
| refundReason | TEXT | Refund reason |
| created_at | timestamp | Creation time |
| updated_at | timestamp | Update time |

# 3. SuperPayACQP API Design Specification

## Overview

This chapter describes the API design specification for the SuperPayACQP payment endpoints. These endpoints implement an acquiring partner system that integrates with Alipay+ payment network, supporting payment processing, cancellation, refund, inquiry, and notification workflows.

## 3.1 SuperPayACQP Endpoints

**Base URL:** `http://localhost:8000`

**Common Request Headers:**

| Header | Required | Description |
|--------|----------|-------------|
| `Content-Type` | Yes | Must be `application/json` |
| `Merchant-ID` | Yes | Merchant ID for authentication |

**Common Response Headers:**

| Header | Description |
|--------|-------------|
| `Content-Type` | Must be `application/json` |

### 3.1.1 Place Order API

#### 3.1.1.1 API Endpoint

```
POST /api/place-order
```

#### 3.1.1.2 Description

The place order API is used by the merchant to send a request to SuperPayACQP to place an order.

#### 3.1.1.3 Request Body

```json
{
  "order": {
    "referenceOrderId": "string",
    "orderDescription": "string",
    "orderAmount": {
      "currency": "string",
      "value": 100
    },
    "paymentFactor": {
      "isInStorePayment": false,
      "isCashierPayment": false,
      "inStorePaymentScenario": "string"
    },
    "merchantId": "string",
    "goods": [
      {
        "referenceGoodsId": "string",
        "goodsName": "string",
        "goodsCategory": "string",
        "goodsBrand": "string",
        "goodsUnitAmount": {
          "currency": "string",
          "value": 100
        },
        "goodsQuantity": 1
      }
    ],
    "shipping": {
      "shippingName": {
        "middleName": "string",
        "firstName": "string",
        "lastName": "string",
        "fullName": "string"
      },
      "shippingPhoneNo": "string",
      "shippingAddress": {
        "region": "string",
        "city": "string",
        "state": "string",
        "address1": "string",
        "address2": "string",
        "zipCode": "string"
      },
      "shippingCarrier": "string"
    },
    "buyer": {
      "referenceBuyerId": "string",
      "buyerName": {
        "middleName": "string",
        "firstName": "string",
        "lastName": "string",
        "fullName": "string"
      },
      "buyerPhoneNo": "string",
      "buyerEmail": "string"
    },
    "env": {
      "terminalType": "string",
      "osType": "string",
      "deviceTokenId": "string",
      "cookieId": "string",
      "clientIp": "string",
      "userAgent": "string",
      "storeTerminalId": "string",
      "storeTerminalRequestTime": "2019-11-27T12:01:01+08:00"
    }
  }
}
```

#### 3.1.1.4 Response Body

Same as [Alipay+ Pay API Response Body](#3224-response-body).

#### 3.1.1.5 Field Mapping

The following fields are auto-generated or have default values when SuperPayACQP calls the Alipay+ Pay API:

| Field | Value | Description |
|-------|-------|-------------|
| `paymentRequestId` | Auto-generated | Unique identifier generated by SuperPayACQP |
| `paymentMethod.paymentMethodType` | `CONNECT_WALLET` | Fixed value |
| `paymentMethod.paymentMethodId` | Empty | Left blank for now |
| `paymentMethod.customerId` | Empty | Left blank for now |
| `paymentMethod.paymentMethodMetaData` | Empty | Left blank for now |
| `paymentExpiryTime` | Current time + 1 minute | Auto-calculated |
| `paymentNotifyUrl` | Empty | Left blank for now |
| `paymentRedirectUrl` | Empty | Left blank for now |

#### 3.1.1.6 Processing Logic

1. SIGNATURE GENERATION
2. SEND REQUEST TO ALIPAY+
3. RECEIVE RESPONSE FROM ALIPAY+
4. VALIDATE RESPONSE SIGNATURE
5. PROCESS RESULT CODE (refer to [Result Codes Processing Logic for Alipay+ Pay API](#3117-result-codes-processing-logic-for-alipay-pay-api))
6. Create a record in api_records table with the message_type of OUTBOUND
7. Return response message to merchant

#### 3.1.1.7 Result Codes Processing Logic for Alipay+ Pay API

1. If resultStatus is 'S' & resultCode is SUCCESS:
   - Return the result code for `SUCCESS` in the response message

2. If resultStatus is 'F' & resultCode is ORDER_IS_CLOSED:
   - Return the result code for `ORDER_IS_CLOSED` in the response message

3. If resultStatus is 'F' & resultCode is OTHER THAN ORDER_IS_CLOSED:
   - Return the result code as per the result of the Alipay+ Pay API in the response message

4. If resultStatus is 'U' & resultCode is PAYMENT_IN_PROCESS:
   - Call the inquiryPayment API to inquire the payment result
   - Retry exactly **10 times** with intervals: **2s, 2s, 3s, 3s, 5s, 5s, 10s, 10s, 10s, 10s**
   - If all retries return 'U', stop calling the inquiryPayment API and return the last response to the merchant

5. If resultStatus is 'U' & resultCode is UNKNOWN_EXCEPTION:
   - Recall the PAY API with the same parameters

6. If resultStatus is 'F' & resultCode is REPEAT_REQ_INCONSISTENT:
   - Return the result code as per the result of the Alipay+ Pay API in the response message

### 3.1.2 Cancel Payment API

#### 3.1.2.1 API Endpoint

```
POST /api/cancel-payment
```

#### 3.1.2.2 Description

The cancel payment API is used by the merchant to send a request to SuperPayACQP to cancel a payment.

#### 3.1.2.3 Request Body

Same as [Alipay+ cancelPayment Request Body](#3223-request-body).

#### 3.1.2.4 Response Body

Same as [Alipay+ cancelPayment Response Body](#3224-response-body).

#### 3.1.2.5 Processing Logic

1. SIGNATURE GENERATION
2. SEND REQUEST TO ALIPAY+
3. RECEIVE RESPONSE FROM ALIPAY+
4. VALIDATE RESPONSE SIGNATURE
5. PROCESS RESULT CODE (refer to [Result Codes Processing Logic for Alipay+ cancelPayment API](#3126-result-codes-processing-logic-for-alipay-cancelpayment-api))
6. Create a record in api_records table with the message_type of OUTBOUND
7. Return response message to merchant

#### 3.1.2.6 Result Codes Processing Logic for Alipay+ cancelPayment API

1. If resultStatus is 'S' & resultCode is SUCCESS:
   - Return the result code for `SUCCESS` in the response message

2. If resultStatus is 'F' & resultCode is CANCEL_WINDOW_EXCEED:
   - Return the result code as per the result of the Alipay+ cancelPayment API in the response message

3. If resultStatus is 'F' & resultCode is OTHER THAN CANCEL_WINDOW_EXCEED:
   - Return the result code as per the result of the Alipay+ cancelPayment API in the response message

4. If resultStatus is 'U' & resultCode is UNKNOWN_EXCEPTION:
   - Recall the cancelPayment API with the same parameters
   - Retry for **60 seconds** with an interval of **10 seconds**
   - After 60 seconds of failed retries, stop the retries and return the response of the last API call to the merchant

### 3.1.3 Refund API

#### 3.1.3.1 API Endpoint

```
POST /api/refund
```

#### 3.1.3.2 Description

The refund API is used by the merchant to send a request to SuperPayACQP to initiate a refund request.

#### 3.1.3.3 Request Body

Same as [Alipay+ Refund Request Body](#3233-request-body).

#### 3.1.3.4 Response Body

Same as [Alipay+ Refund Response Body](#3234-response-body).

#### 3.1.3.5 Processing Logic

1. SIGNATURE GENERATION
2. SEND REQUEST TO ALIPAY+
3. RECEIVE RESPONSE FROM ALIPAY+
4. VALIDATE RESPONSE SIGNATURE
5. PROCESS RESULT CODE (refer to [Result Codes Processing Logic for Alipay+ Refund API](#3136-result-codes-processing-logic-for-alipay-refund-api))
6. Create a record in api_records table with the message_type of OUTBOUND
7. Return response message to merchant

#### 3.1.3.6 Result Codes Processing Logic for Alipay+ Refund API

1. If resultStatus is 'S' & resultCode is SUCCESS:
   - Return the result code for `SUCCESS` in the response message

2. If resultStatus is 'F':
   - Return the result code as per the result of the Alipay+ refund API in the response message

3. If resultStatus is 'U' & resultCode is UNKNOWN_EXCEPTION:
   - Return the result code as per the result of the Alipay+ refund API in the response message

### 3.1.4 InquiryPayment API

#### 3.1.4.1 API Endpoint

```
POST /api/inquiryPayment
```

#### 3.1.4.2 Description

The inquiry payment API is used by the merchant to send a request to SuperPayACQP to query the payment result.

#### 3.1.4.3 Request Body

Same as [Alipay+ InquiryPayment Request Body](#3243-request-body).

#### 3.1.4.4 Response Body

Same as [Alipay+ InquiryPayment Response Body](#3244-response-body).

#### 3.1.4.5 Processing Logic

1. SIGNATURE GENERATION
2. SEND REQUEST TO ALIPAY+
3. RECEIVE RESPONSE FROM ALIPAY+
4. VALIDATE RESPONSE SIGNATURE
5. PROCESS RESULT CODE (refer to [Result Codes Processing Logic for Alipay+ InquiryPayment API](#3146-result-codes-processing-logic-for-alipay-inquirypayment-api))
6. Create a record in api_records table with the message_type of OUTBOUND
7. Return response message to merchant

#### 3.1.4.6 Result Codes Processing Logic for Alipay+ InquiryPayment API

1. If resultStatus is 'S' & resultCode is SUCCESS:
   - Return the result code for `SUCCESS` in the response message

2. If resultStatus is 'F':
   - Return the result code as per the result of the Alipay+ inquiryPayment API in the response message

3. If resultStatus is 'U' & resultCode is UNKNOWN_EXCEPTION:
   - Retry to call the inquiryPayment API with the same parameters with an interval of **5 seconds**
   - Continue retrying until the `payment_requests.paymentExpiryTime` is before the current time
   - When expiry time is reached, return the response of the last API call to the merchant
   - **Trigger automatic cancelPayment API call** to cancel the payment

### 3.1.5 NotifyPayment Endpoint

#### 3.1.5.1 API Endpoint

```
POST /alipay/notifyPayment
```

#### 3.1.5.2 Description

The notifyPayment is an endpoint that SuperPayACQP receives payment result notifications sent from Alipay+.

#### 3.1.5.3 Request Body

```json
{
  "paymentResult": {
    "resultCode": "string",
    "resultStatus": "S|F|U",
    "resultMessage": "string"
  },
  "paymentRequestId": "string",
  "paymentId": "string",
  "acquirerId": "string",
  "pspId": "string",
  "customerId": "string",
  "walletBrandName": "string",
  "paymentAmount": {
    "currency": "string",
    "value": 100
  },
  "paymentTime": "string (ISO 8601)",
  "settlementAmount": {
    "currency": "string",
    "value": 100
  },
  "settlementQuote": {
    "quoteId": "string",
    "quoteCurrencyPair": "string",
    "quotePrice": 1.0,
    "quoteStartTime": "string (ISO 8601)",
    "quoteExpiryTime": "string (ISO 8601)",
    "quoteUnit": "string",
    "baseCurrency": "string"
  },
  "customsDeclarationAmount": {
    "currency": "string",
    "value": 100
  },
  "mppPaymentId": "string"
}
```

#### 3.1.5.4 Expected Response

The SuperPayACQP should respond with:

```json
{
  "result": {
    "resultCode": "string",
    "resultStatus": "S|F|U",
    "resultMessage": "string"
  }
}
```

#### 3.1.5.5 Processing Logic

1. VALIDATE REQUEST SIGNATURE (refer to [Request Signature Verification](#34-request-signature-verification))
2. PROCESS THE PAYMENT NOTIFICATION
3. Create a record in api_records table with the message_type of **INBOUND**
4. Return response message to Alipay+

## 3.2 Alipay+ API

**Base URL:** `https://open-sea.alipayplus.com/aps`

**Common Headers:**

| Header | Required | Description |
|--------|----------|-------------|
| `Signature` | Yes | Request signature for authentication |
| `Request-Time` | Yes | Timestamp of the request |
| `Content-Type` | Yes | Must be `application/json` |

**Common Response Headers:**

| Header | Description |
|--------|-------------|
| `Client-Id` | The client identifier |
| `Signature` | Response signature |
| `response-time` | Response timestamp |

---

## Result Status Codes

All API responses include a `result` object with the following status values:

| Status | Meaning |
|--------|---------|
| `S` | Success - The operation completed successfully |
| `F` | Failure - The operation failed, do not retry |
| `U` | Unknown - The operation status is unknown, retry may be appropriate |

### Common Result Codes

| Result Code | Status | Description |
|-------------|--------|-------------|
| `SUCCESS` | S | Operation successful |
| `INVALID_SIGNATURE` | F | The signature verification failed |
| `PROCESS_FAIL` | F | General business failure |
| `ORDER_IS_CLOSED` | F | The order has been closed/cancelled |
| `REPEAT_REQ_INCONSISTENT` | F | Repeated request with different parameters |
| `UNKNOWN_EXCEPTION` | U | Unknown error occurred |
| `PAYMENT_IN_PROCESS` | U | Payment is still being processed |

---

### 3.2.1 Alipay+ Pay API

#### 3.2.1.1 API Endpoint

```
POST /aps/api/v1/payments/pay
```

#### 3.2.1.2 Description

The pay API is used by the Acquiring Service Provider (ACQP) to send a request to Alipay+ to deduct funds from the user's mobile payment provider (MPP) account.

#### 3.2.1.3 Request Body

```json
{
  "paymentRequestId": "string",
  "paymentAmount": {
    "currency": "string",
    "value": 100
  },
  "paymentMethod": {
    "paymentMethodType": "string",
    "paymentMethodId": "string",
    "customerId": "string",
    "paymentMethodMetaData": {
      "authClientId": "string"
    }
  },
  "paymentFactor": {
    "isInStorePayment": false,
    "isCashierPayment": false,
    "inStorePaymentScenario": "string"
  },
  "paymentExpiryTime": "string (ISO 8601)",
  "paymentNotifyUrl": "string",
  "paymentRedirectUrl": "string",
  "splitSettlementId": "string",
  "settlementStrategy": {
    "settlementCurrency": "string"
  },
  "order": {
    "referenceOrderId": "string",
    "orderDescription": "string",
    "orderAmount": {
      "currency": "string",
      "value": 100
    },
    "merchant": {
      "referenceMerchantId": "string",
      "merchantName": "string",
      "merchantDisplayName": "string",
      "merchantRegisterDate": "2019-11-27T12:01:01+08:00",
      "merchantMCC": "string",
      "merchantAddress": {
        "region": "string",
        "city": "string",
        "state": "string",
        "address1": "string",
        "address2": "string",
        "zipCode": "string"
      },
      "store": {
        "referenceStoreId": "string",
        "storeName": "string",
        "storeMCC": "string",
        "storeDisplayName": "string",
        "storeTerminalId": "string",
        "storeOperatorId": "string",
        "storePhoneNo": "string",
        "storeAddress": {
          "region": "string",
          "city": "string",
          "state": "string",
          "address1": "string",
          "address2": "string",
          "zipCode": "string"
        }
      }
    },
    "goods": [
      {
        "referenceGoodsId": "string",
        "goodsName": "string",
        "goodsCategory": "string",
        "goodsBrand": "string",
        "goodsUnitAmount": {
          "currency": "string",
          "value": 100
        },
        "goodsQuantity": 1
      }
    ],
    "shipping": {
      "shippingName": {
        "middleName": "string",
        "firstName": "string",
        "lastName": "string",
        "fullName": "string"
      },
      "shippingPhoneNo": "string",
      "shippingAddress": {
        "region": "string",
        "city": "string",
        "state": "string",
        "address1": "string",
        "address2": "string",
        "zipCode": "string"
      },
      "shippingCarrier": "string"
    },
    "buyer": {
      "referenceBuyerId": "string",
      "buyerName": {
        "middleName": "string",
        "firstName": "string",
        "lastName": "string",
        "fullName": "string"
      },
      "buyerPhoneNo": "string",
      "buyerEmail": "string"
    },
    "env": {
      "terminalType": "string",
      "osType": "string",
      "deviceTokenId": "string",
      "cookieId": "string",
      "clientIp": "string",
      "userAgent": "string",
      "storeTerminalId": "string",
      "storeTerminalRequestTime": "2019-11-27T12:01:01+08:00"
    },
    "indirectAcquirer": {
      "referenceAcquirerId": "string",
      "acquirerName": "string",
      "acquirerAddress": {
        "region": "string",
        "city": "string",
        "state": "string",
        "address1": "string",
        "address2": "string",
        "zipCode": "string"
      }
    }
  }
}
```

#### 3.2.1.4 Response Body

```json
{
  "result": {
    "resultCode": "string",
    "resultStatus": "S|F|U",
    "resultMessage": "string"
  },
  "acquirerId": "string",
  "paymentId": "string",
  "paymentTime": "string (ISO 8601)",
  "paymentAmount": {
    "currency": "string",
    "value": 100
  },
  "customerId": "string",
  "pspId": "string",
  "walletBrandName": "string",
  "settlementAmount": {
    "currency": "string",
    "value": 100
  },
  "settlementQuote": {
    "quoteId": "string",
    "quoteCurrencyPair": "string",
    "quotePrice": 1.0,
    "quoteStartTime": "string (ISO 8601)",
    "quoteExpiryTime": "string (ISO 8601)",
    "quoteUnit": "string",
    "baseCurrency": "string"
  },
  "customsDeclarationAmount": {
    "currency": "string",
    "value": 100
  },
  "mppPaymentId": "string"
}
```

### 3.2.2 Alipay+ cancelPayment Endpoint

#### 3.2.2.1 Endpoint

```
POST /aps/api/v1/payments/cancelPayment
```

#### 3.2.2.2 Description

The Acquiring Partner (ACQP) uses the cancelPayment API to proactively cancel a payment when no payment result is received after the payment expires, or when the ACQP has closed the payment already.

#### 3.2.2.3 Request Body

```json
{
  "paymentId": "string",
  "paymentRequestId": "string"
}
```

#### 3.2.2.4 Response Body

```json
{
  "result": {
    "resultCode": "string",
    "resultStatus": "S|F|U",
    "resultMessage": "string"
  },
  "pspId": "string",
  "acquirerId": "string"
}
```

### 3.2.3 Alipay+ Refund Endpoint

#### 3.2.3.1 Endpoint

```
POST /aps/api/v1/payments/refund
```

#### 3.2.3.2 Description

The Acquiring Partner (ACQP) uses the refund API to initiate a refund of a successful payment.

The refund can be full or partial. A transaction can have multiple refunds as long as the total refund amount is less than or equal to the original transaction amount.

#### 3.2.3.3 Request Body

```json
{
  "paymentRequestId": "string",
  "paymentId": "string",
  "refundRequestId": "string",
  "refundAmount": {
    "currency": "string",
    "value": 100
  },
  "refundReason": "string"
}
```

#### 3.2.3.4 Response Body

```json
{
  "result": {
    "resultCode": "string",
    "resultStatus": "S|F|U",
    "resultMessage": "string"
  },
  "acquirerId": "string",
  "pspId": "string",
  "refundId": "string",
  "refundTime": "string (ISO 8601)",
  "refundAmount": {
    "currency": "string",
    "value": 100
  },
  "settlementAmount": {
    "currency": "string",
    "value": 100
  },
  "settlementQuote": {
    "quoteId": "string",
    "quoteCurrencyPair": "string",
    "quotePrice": 1.0,
    "quoteStartTime": "string (ISO 8601)",
    "quoteExpiryTime": "string (ISO 8601)",
    "quoteUnit": "string",
    "baseCurrency": "string"
  }
}
```

### 3.2.4 InquiryPayment Endpoint

#### 3.2.4.1 Endpoint

```
POST /aps/api/v1/payments/inquiryPayment
```

#### 3.2.4.2 Description

The inquiryPayment API is used by the Acquiring Service Provider (ACQP) to query the payment result if no payment result is received after a certain period of time.

#### 3.2.4.3 Request Body

```json
{
  "paymentId": "string",
  "paymentRequestId": "string"
}
```

#### 3.2.4.4 Response Body

```json
{
  "result": {
    "resultCode": "string",
    "resultStatus": "S|F|U",
    "resultMessage": "string"
  },
  "paymentResult": {
    "resultCode": "string",
    "resultStatus": "S|F|U",
    "resultMessage": "string"
  },
  "acquirerId": "string",
  "pspId": "string",
  "paymentRequestId": "string",
  "paymentId": "string",
  "paymentAmount": {
    "currency": "string",
    "value": 100
  },
  "paymentTime": "string (ISO 8601)",
  "customerId": "string",
  "walletBrandName": "string",
  "settlementAmount": {
    "currency": "string",
    "value": 100
  },
  "settlementQuote": {
    "quoteId": "string",
    "quoteCurrencyPair": "string",
    "quotePrice": 1.0,
    "quoteStartTime": "string (ISO 8601)",
    "quoteExpiryTime": "string (ISO 8601)",
    "quoteUnit": "string",
    "baseCurrency": "string"
  },
  "customsDeclarationAmount": {
    "currency": "string",
    "value": 100
  },
  "mppPaymentId": "string",
  "transactions": [
    {
      "transactionResult": {
        "resultCode": "string",
        "resultStatus": "S|F|U",
        "resultMessage": "string"
      },
      "transactionId": "string",
      "transactionRequestId": "string",
      "transactionAmount": {
        "currency": "string",
        "value": 100
      },
      "transactionTime": "string (ISO 8601)",
      "transactionType": "string",
      "transactionStatus": "string"
    }
  ]
}
```

## 3.3 Security

### 3.3.1 Overview

All Alipay+ API requests and responses are secured using **RSA-SHA256 digital signatures**.

### 3.3.2 Cryptographic Algorithm

| Property | Value |
|----------|-------|
| **Signature Algorithm** | `SHA256withRSA` |
| **Key Algorithm** | RSA |
| **Key Format (Private)** | PKCS#8 (Base64 encoded) |
| **Key Format (Public)** | X.509 (Base64 encoded) |
| **Encoding** | UTF-8 |
| **Signature Encoding** | Base64 + URL encoding |

---

### 3.3.3 Request Signing

When SuperPayACQP sends a request to the Alipay+, the request must be signed using the SuperPayACQP's private key.

#### 3.3.3.1 Signature Header Format

```
Signature: algorithm=RSA256,keyVersion=1,signature=<url-encoded-base64-signature>
```

#### 3.3.3.2 Required Headers for Signed Requests

| Header | Description | Example |
|--------|-------------|---------|
| `Signature` | The signature header with algorithm and signature value | `algorithm=RSA256,keyVersion=1,signature=...` |
| `Client-Id` | The client identifier | `CLIENT_001` |
| `Request-Time` | UTC timestamp of the request | `2024-01-15T10:30:00Z` |
| `Content-Type` | Content type | `application/json; charset=UTF-8` |

#### 3.3.3.3 Signature Generation Process

```
┌─────────────────────────────────────────────────────────────────┐
│                  REQUEST SIGNATURE GENERATION                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  INPUT:                                                         │
│    - httpMethod: "POST"                                         │
│    - requestUri: "/aps/api/v1/payments/pay"                     │
│    - requestTime: "2024-01-15T10:30:00Z"                        │
│    - requestBody: {"paymentRequestId":"xxx",...}                │
│    - clientId: "CLIENT_001"                                     │
│    - privateKey: (Base64 encoded PKCS#8 private key)            │
│                                                                 │
│  STEP 1: Build Content to Be Signed                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Format:                                                   │  │
│  │    HTTP_METHOD URI                                         │  │
│  │    ClientId.RequestTime.RequestBody                        │  │
│  │                                                            │  │
│  │  Example:                                                  │  │
│  │    POST /aps/api/v1/payments/pay                           │  │
│  │    CLIENT_001.2024-01-15T10:30:00Z.{"paymentRequestId":... │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  STEP 2: Sign the Content                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  1. Load private key from Base64 encoded PKCS#8 format    │  │
│  │  2. Initialize Signature with SHA256withRSA algorithm     │  │
│  │  3. Update signature with content bytes (UTF-8)           │  │
│  │  4. Generate signature bytes                              │  │
│  │  5. Base64 encode the signature bytes                     │  │
│  │  6. URL encode the Base64 string                          │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  STEP 3: Build Signature Header                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Signature: algorithm=RSA256,keyVersion=1,signature=<sig> │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  OUTPUT:                                                        │
│    - Signature header value                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 3.3.3.4 Content to Be Signed Format

```
POST /aps/api/v1/payments/pay
CLIENT_001.2024-01-15T10:30:00Z.{"paymentRequestId":"pay-123","paymentAmount":{"currency":"MYR","value":1000}}
```

**Format Specification:**
```
<HTTP_METHOD> <REQUEST_URI>
<CLIENT_ID>.<REQUEST_TIME>.<REQUEST_BODY>
```

Where:
- `HTTP_METHOD`: Uppercase HTTP method (e.g., `POST`)
- `REQUEST_URI`: The API endpoint path (e.g., `/aps/api/v1/payments/pay`)
- `CLIENT_ID`: The client identifier from configuration
- `REQUEST_TIME`: UTC timestamp in format `yyyy-MM-dd'T'HH:mm:ss'Z'`
- `REQUEST_BODY`: The raw JSON request body (or empty string if null)

#### 3.3.3.5 Sample Java Implementation

```java
public String generateRequestSignature(String httpMethod, String requestUri,
                                        String requestTime, String requestBody) {
    // Step 1: Build content to be signed
    String contentToBeSigned = String.format("%s %s\n%s.%s.%s",
        httpMethod.toUpperCase(),
        requestUri,
        this.config.getClientId(),
        requestTime,
        requestBody != null ? requestBody : ""
    );

    // Step 2: Load private key
    byte[] keyBytes = Base64.getDecoder().decode(privateKeyStr);
    PKCS8EncodedKeySpec keySpec = new PKCS8EncodedKeySpec(keyBytes);
    KeyFactory keyFactory = KeyFactory.getInstance("RSA");
    PrivateKey privateKeyObj = keyFactory.generatePrivate(keySpec);

    // Step 3: Sign the content
    Signature signature = Signature.getInstance("SHA256withRSA");
    signature.initSign(privateKeyObj);
    signature.update(contentToBeSigned.getBytes(StandardCharsets.UTF_8));
    byte[] signatureBytes = signature.sign();

    // Step 4: Encode and return
    return URLEncoder.encode(
        Base64.getEncoder().encodeToString(signatureBytes),
        StandardCharsets.UTF_8.name()
    );
}
```

---

### 3.3.4 Request Signature Verification

When SuperPayACQP receives a request from Alipay+ (e.g., notifyPayment), it verifies the signature using the Alipay+ public key.

#### 3.3.4.1 Verification Process

```
┌─────────────────────────────────────────────────────────────────┐
│                 REQUEST SIGNATURE VERIFICATION                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  INPUT:                                                         │
│    - Signature header from request                              │
│    - Request-Time header                                        │
│    - Request URI                                                │
│    - Request body                                               │
│    - Alipay+ public key                                         │
│                                                                 │
│  STEP 1: Extract Signature Value                                │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Header: Signature: algorithm=RSA256,keyVersion=1,        │  │
│  │         signature=abc123...                               │  │
│  │                                                            │  │
│  │  Parse and extract: signature=abc123...                   │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  STEP 2: Build Content to Be Validated                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Same format as signing:                                  │  │
│  │    POST /alipay/notifyPayment                             │  │
│  │    CLIENT_001.2024-01-15T10:30:00Z.{"paymentRequestId":...│  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  STEP 3: Verify Signature                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  1. Load public key from Base64 encoded X.509 format     │  │
│  │  2. URL decode the signature value                        │  │
│  │  3. Base64 decode to get signature bytes                 │  │
│  │  4. Initialize Signature for verification                │  │
│  │  5. Update with content bytes (UTF-8)                    │  │
│  │  6. Verify signature bytes                               │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  OUTPUT:                                                        │
│    - true: Signature is valid                                   │
│    - false: Signature is invalid or verification failed         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 3.3.4.2 Sample Java Implementation

```java
public boolean verifyRequestSignature(String httpMethod, String requestUri,
                                       String requestTime, String requestBody,
                                       String requestSignature) {
    if (requestSignature == null || requestSignature.isBlank()) {
        return false;
    }

    try {
        // Step 1: Build content to be validated
        String contentToBeValidated = String.format("%s %s\n%s.%s.%s",
            httpMethod.toUpperCase(),
            requestUri,
            this.config.getClientId(),
            requestTime,
            requestBody != null ? requestBody : ""
        );

        // Step 2: Load public key
        byte[] keyBytes = Base64.getDecoder().decode(publicKeyStr);
        X509EncodedKeySpec keySpec = new X509EncodedKeySpec(keyBytes);
        KeyFactory keyFactory = KeyFactory.getInstance("RSA");
        PublicKey publicKeyObj = keyFactory.generatePublic(keySpec);

        // Step 3: Verify signature
        Signature signature = Signature.getInstance("SHA256withRSA");
        signature.initVerify(publicKeyObj);
        signature.update(contentToBeValidated.getBytes(StandardCharsets.UTF_8));

        // Step 4: Decode and verify
        byte[] signatureBytes = Base64.getDecoder().decode(
            URLDecoder.decode(requestSignature, StandardCharsets.UTF_8.name())
        );

        return signature.verify(signatureBytes);

    } catch (Exception e) {
        return false;
    }
}
```

#### 3.3.4.3 Extracting Signature from Header

```java
public String extractSignatureFromResponse(String signatureHeader) {
    String signatureValue = null;
    for (String part : signatureHeader.split(",")) {
        String trimmed = part.trim();
        if (trimmed.startsWith("signature=")) {
            signatureValue = trimmed.substring("signature=".length());
            break;
        }
    }
    return signatureValue;
}
```

---

### 3.3.5 Response Signing

When SuperPayACQP sends a response, it signs the response using its private key.

#### 3.3.5.1 Response Signature Header Format

```
Signature: algorithm=RSA256,keyVersion=0,clientId=<CLIENT_ID>,signature=<url-encoded-base64-signature>
```

#### 3.3.5.2 Response Headers

| Header | Description | Example |
|--------|-------------|---------|
| `Signature` | The signature header | `algorithm=RSA256,keyVersion=0,clientId=CLIENT_001,signature=...` |
| `response-time` | UTC timestamp of the response | `2024-01-15T10:30:01Z` |
| `Client-Id` | The client identifier | `CLIENT_001` |
| `Content-Type` | Content type | `application/json` |

#### 3.3.5.3 Response Signature Generation

The process is identical to request signing, but uses:
- `responseTime` instead of `requestTime`
- `responseBody` instead of `requestBody`
- `responseUri` (same as request URI)

#### 3.3.5.4 Sample Java Implementation

```java
public HttpHeaders getResponseHttpHeaders(String responseBody,
                                           String HTTP_METHOD,
                                           String RESPONSE_URI) {
    // Generate response timestamp
    String responseTime = ZonedDateTime.now(ZoneOffset.UTC)
        .format(DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss'Z'"));

    // Generate signature
    String signature = signatureService.generateRequestSignature(
        HTTP_METHOD, RESPONSE_URI, responseTime, responseBody);

    // Build signature header
    String authHeader = String.format(
        "algorithm=RSA256,keyVersion=0,clientId=%s,signature=%s",
        this.config.getClientId(), signature);

    // Build headers
    HttpHeaders headers = new HttpHeaders();
    headers.setContentType(MediaType.APPLICATION_JSON);
    headers.set("Signature", authHeader);
    headers.set("response-time", responseTime);

    return headers;
}
```

---

### 3.3.6 Response Signature Verification

When SuperPayACQP receives a response from Alipay+, it should verify the signature.

#### 3.3.6.1 Verification Process

Same as request verification, but using:
- Response body
- Response URI
- `response-time` header value
- Alipay+ public key

```
┌─────────────────────────────────────────────────────────────────┐
│                RESPONSE SIGNATURE VERIFICATION                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  STEP 1: Extract signature from response header                 │
│                                                                 │
│  STEP 2: Build content to validate                              │
│          POST /aps/api/v1/payments/pay                          │
│          CLIENT_001.2024-01-15T10:30:01Z.{"result":{...}}       │
│                                                                 │
│  STEP 3: Verify using Alipay+ public key                        │
│                                                                 │
│  RESULT:                                                        │
│    - Valid: Response is authentic and untampered                │
│    - Invalid: Response may be forged or modified                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### 3.3.7 Key Management

#### Private Key Format (PKCS#8)

```
-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC...
(Base64 encoded key bytes)
-----END PRIVATE KEY-----
```

For storage in configuration, remove the header/footer and store as Base64:
```
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC...
```

#### Public Key Format (X.509)

```
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
(Base64 encoded key bytes)
-----END PUBLIC KEY-----
```

For storage in configuration, remove the header/footer and store as Base64:
```
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
```

#### Key Loading

```java
// Load Private Key (PKCS#8 format)
private PrivateKey loadPrivateKey(String privateKeyStr) throws Exception {
    byte[] keyBytes = Base64.getDecoder().decode(privateKeyStr);
    PKCS8EncodedKeySpec keySpec = new PKCS8EncodedKeySpec(keyBytes);
    KeyFactory keyFactory = KeyFactory.getInstance("RSA");
    return keyFactory.generatePrivate(keySpec);
}

// Load Public Key (X.509 format)
private PublicKey loadPublicKey(String publicKeyStr) throws Exception {
    byte[] keyBytes = Base64.getDecoder().decode(publicKeyStr);
    X509EncodedKeySpec keySpec = new X509EncodedKeySpec(keyBytes);
    KeyFactory keyFactory = KeyFactory.getInstance("RSA");
    return keyFactory.generatePublic(keySpec);
}
```

---

### Security Best Practices

1. **Key Storage**
   - Store private keys securely (environment variables, secret management)
   - Never commit private keys to version control
   - Rotate keys periodically

2. **Timestamp Validation**
   - Validate that `Request-Time` is within acceptable time window (e.g., ±5 minutes)
   - Prevents replay attacks

3. **Signature Validation Failure**
   - Return `INVALID_SIGNATURE` error with status `F`
   - Log the failure for security monitoring
   - Do not process the request

4. **HTTPS**
   - Always use HTTPS in production
   - Signatures provide additional security layer on top of TLS

## 3.4 Error Handling

### 3.4.1 HTTP Status Codes

SuperPayACQP returns the following HTTP status codes to merchants:

| HTTP Status Code | Description |
|------------------|-------------|
| `200 OK` | Request processed successfully |
| `400 Bad Request` | Invalid request format or Alipay+ unavailability |
| `403 Forbidden` | Merchant authentication failure |
| `500 Internal Server Error` | Internal system errors |

### 3.4.2 Error Response Format

All errors follow the standard result format:

```json
{
  "result": {
    "resultCode": "ERROR_CODE",
    "resultStatus": "F|U",
    "resultMessage": "Human-readable error message"
  }
}
```

### 3.4.3 Timeout and Retry Logic

When Alipay+ doesn't respond within a timeout period or network connectivity issues occur:

1. Retry the API call with the same parameters
2. Follow the retry logic specified in each API's result codes processing section
3. If all retries fail, return the last response to the merchant

# 4. References

| Reference | Value |
|-----------|-------|
| Alipay+ Public Key | MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAtXbe4yU4x1XbpXcwNfynVgo4+RHc/vhV90ImyAqLabvXQlS5/JQQ+gKaO3R5qqu9E0AlWTL/uzFKnlxqkAwjePD9UC1UEkgWqxsM+ZzEuZF1Urd7klHBt4VUItHocoPJinFkIDX+EnbkObCXq80aPUg438ouGXE8c18rlmBmUk+08Y3VrH/O0+yxPXOkbA0El1B/ILZlCrgMKUx6cqwv5XX7YgCSGxwEtuLGFeGZnJHPcfOo6hJoGdXuE0Wi0vO5lwobxszMcAyq6Rkf+AzoR0ziE+5kvsqowl6WP7rqSPuOYPqxvl4u4eqU+qkWAzSwqxPnTa1zHyhAqraUwM3AaQIDAQAB

| Client-Id | SANDBOX_5YHQ7N30CPL702872 |
| private key | MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCKkMvH8hBhjOWJRAQPNBIqKgXfvYm4LYEjlUoPZtmTt4NFY/llfd6wNlHM5KpmZB4oTsyDgmvnZqzm0yZ4D4YMFlJe2ziuX9BKRTXXLniKJ+gXM5BflFLHMxlx2UzspKIlQ5guafULqtATAaHBlTdOLTuSJDlxM/Iu0zvaRftz9cY2zR1Nf5Yd7Nghw4B4zxtfgM2x1pnHN/H/tHvaVNCMk4NkYb+1ZyNjxMQ4jnMcXtLgIWzzNUTiw1+CnH00j4uyN5zdiD6EkMUGEQ0njPegZuxnCfUkq1ljP53dJqh5kNU9ih+Piv3LbUweqaZe6vk8bqvnX3DhOlWfkBIc6a9HAgMBAAECggEBAIWvjzv3+f/zzNzzJyt35HKTmpkzp3RvSqGG/i3/37kZm2fOPabCmp/NuHwCvbgNrd7br4rNwMc/k18bpoi9CWoN+yiTPotV24JcZcaWiitYtx3zXL4qPvb7APiLWyEQ8XMcVO2qwoWgJiHAOEypZvNgxpGHq3fhUy4EFEHRtPk5YEYHAdrSXG0Cd12DiV4OVgHweJMD8qEmWzA6UYGTzojYEC0hUwmg4bZgjLbkxGoQQdFs9AnEn11K6gi/EmQQyaQCuaGF26kUWUhA7HDNc7foZy/dIzi4QCNj+e9EeKgcmMaLLZTu/bRDlvpCY19se4OaiJcILNxneYmUfnACQ9ECgYEAzeSK8rJ2Ovd3MtOLqNmvMy6pJa9TLlCQD/5x5wJ8MGygRGwji54q6C/T9LdKbMdg9wXmC4XyQFI/O4ywJgTOb10SYh1LcKLlzJP0GogfY1gVTqxCzntFaQBBxOVWGyIf0aP0IjRtBsWGDmeGEwhDT0e59hWY8OugWGTyJnW6Nj8CgYEArEmpaisDoEPvYPRGZenTY5FoZd33jV8g4AO9bB3v9D5ao7PTIxHlMHbpD5M0MmMtAuVmP0OtnhQF95h08Q9HRJ1bn0fwNnpSpR6ZIQPF+FBqdoxsFOJVjujqoG4QylBSm7QpiN02yhjJG+7aST4cohzxQ09Hv9OTAmMLNHnyFPkCgYEAngVJK0oS+eDSSF0aNEaWc8bdJUIxqjtExjG4Q9+hZx0HyFvi0BZdwgRrPcerRF+lqRGK5M8yBXHafB7XVuabdddN86WeL92mV2Q6ll5hEMMa313QjF8J/7OlxrNpabvABgs6pUHtZ6QT5lxIB7Vwy5k2PYuH7Wg6kX0waJo0h8sCgYBDywh62kom+hRrljNNTuD7QPBPhTQv0Mri2xXiQTV2akLIP65JEnWYyHGUy1uyqAvCI/pD0qGynjZq4vbBFD365eBzoJ8JEMEMcCnZL97qgtoho8ezwAvinAwW7Lh2o3yeABqH3GP+yhn4f9gtEd+6eqEE12FoPhyOx+JU19dGIQKBgEP4yFkcp0nsUGLgDw+trLPmgx98rLRFHtyuOdpwFF7G3gqJpdFUaaLEEx+HpQvsGL4SY3luT2WGKpNa/+78jm6BBkmKodEVyeXaA7g+HQHFFcam5Zjzix9vqKNd+iOXsmf4psHzC1n8Xo/KnSz/PVC6OZ89YnRml6QcpK4x3+4C
