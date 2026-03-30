"""
Constants and Enums for SuperPayACQP
"""
from enum import Enum
from typing import Optional

from pydantic import BaseModel, field_serializer


class ResultStatus(str, Enum):
    """Result status enumeration"""
    SUCCESS = 'S'
    FAILURE = 'F'
    UNKNOWN = 'U'
    
    @classmethod
    def from_string(cls, value: str) -> 'ResultStatus':
        """
        Convert a string to ResultStatus enum.
        
        Args:
            value: String representation of ResultStatus ('S', 'F', 'U' or 
                   'SUCCESS', 'FAILURE', 'UNKNOWN' - case insensitive)
            
        Returns:
            ResultStatus enum value
            
        Raises:
            ValueError: If the string cannot be converted to a valid ResultStatus
        """
        if not value:
            return cls.UNKNOWN
        
        # Normalize the input - uppercase and strip whitespace
        normalized = value.strip().upper()
        
        # Map of string values to enum
        mapping = {
            'S': cls.SUCCESS,
            'F': cls.FAILURE,
            'U': cls.UNKNOWN,
            'SUCCESS': cls.SUCCESS,
            'FAILURE': cls.FAILURE,
            'UNKNOWN': cls.UNKNOWN,
        }
        
        if normalized in mapping:
            return mapping[normalized]
        
        # If not found, return UNKNOWN as default
        return cls.UNKNOWN


class PaymentStatus(str, Enum):
    PENDING = 'PENDING'
    SUCCESS = 'SUCCESS'
    CANCELLED = 'CANCELLED'
    FAILED = 'FAILED'


class MessageType(str, Enum):
    """API record message type enumeration"""
    INBOUND = 'INBOUND'
    OUTBOUND = 'OUTBOUND'


class HTTPMethod(str, Enum):
    POST = 'POST'
    PUT = 'PUT'
    GET = 'GET'
    DELETE = 'DELETE'
    PATCH = 'PATCH'


class ResultCode(str, Enum):
    """Common result codes"""
    SUCCESS = 'SUCCESS'
    ACCESS_DENIED = 'ACCESS_DENIED'
    BUSINESS_NOT_SUPPORT = 'BUSINESS_NOT_SUPPORT'
    CURRENCY_NOT_SUPPORT = 'CURRENCY_NOT_SUPPORT'
    EXPIRED_CODE = 'EXPIRED_CODE'
    INVALID_CLIENT = 'INVALID_CLIENT'
    INVALID_CODE = 'INVALID_CODE'
    INVALID_CONTRACT = 'INVALID_CONTRACT'
    INVALID_SIGNATURE = 'INVALID_SIGNATURE'
    INVALID_TOKEN = 'INVALID_TOKEN'
    KEY_NOT_FOUND = 'KEY_NOT_FOUND'
    MEDIA_TYPE_NOT_ACCEPTABLE = 'MEDIA_TYPE_NOT_ACCEPTABLE'
    MERCHANT_NOT_REGISTERED = 'MERCHANT_NOT_REGISTERED'
    METHOD_NOT_SUPPORTED = 'METHOD_NOT_SUPPORTED'
    NO_INTERFACE_DEF = 'NO_INTERFACE_DEF'
    ORDER_IS_CLOSED = 'ORDER_IS_CLOSED'
    PARAM_ILLEGAL = 'PARAM_ILLEGAL'
    PAYMENT_AMOUNT_EXCEED_LIMIT = 'PAYMENT_AMOUNT_EXCEED_LIMIT'
    PAYMENT_COUNT_EXCEED_LIMIT = 'PAYMENT_COUNT_EXCEED_LIMIT'
    PROCESS_FAIL = 'PROCESS_FAIL'
    REGULATION_RESTRICTION = 'REGULATION_RESTRICTION'
    REPEAT_REQ_INCONSISTENT = 'REPEAT_REQ_INCONSISTENT'
    RISK_REJECT = 'RISK_REJECT'
    UNAVAILABLE_PAYMENT_METHOD = 'UNAVAILABLE_PAYMENT_METHOD'
    USER_AMOUNT_EXCEED_LIMIT = 'USER_AMOUNT_EXCEED_LIMIT'
    USER_BALANCE_NOT_ENOUGH = 'USER_BALANCE_NOT_ENOUGH'
    USER_KYC_NOT_QUALIFIED = 'USER_KYC_NOT_QUALIFIED'
    USER_NOT_EXIST = 'USER_NOT_EXIST'
    USER_PAYMENT_VERIFICATION_FAILED = 'USER_PAYMENT_VERIFICATION_FAILED'
    USER_STATUS_ABNORMAL = 'USER_STATUS_ABNORMAL'
    PAYMENT_IN_PROCESS = 'PAYMENT_IN_PROCESS'
    REQUEST_TRAFFIC_EXCEED_LIMIT = 'REQUEST_TRAFFIC_EXCEED_LIMIT'
    UNKNOWN_EXCEPTION = 'UNKNOWN_EXCEPTION'
    CANCEL_WINDOW_EXCEED = 'CANCEL_WINDOW_EXCEED'
    REFUND_AMOUNT_EXCEED = 'REFUND_AMOUNT_EXCEED'
    REFUND_WINDOW_EXCEED = 'REFUND_WINDOW_EXCEED'
    ORDER_NOT_EXIST = 'ORDER_NOT_EXIST'
    INVALID_REQUEST = 'INVALID_REQUEST'
    MISSING_MERCHANT_ID = 'MISSING_MERCHANT_ID'
    INVALID_MERCHANT = 'INVALID_MERCHANT'
    INTERNAL_ERROR = 'INTERNAL_ERROR'


class Result(BaseModel):
    """Result model for API responses - Pydantic model for seamless serialization"""
    resultStatus: ResultStatus
    resultMessage: str
    resultCode: str

    @field_serializer('resultStatus')
    def serialize_result_status(self, value: ResultStatus) -> str:
        """Serialize ResultStatus enum to string value"""
        return value.value if isinstance(value, ResultStatus) else value



    @classmethod
    def returnSuccess(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.SUCCESS,
            resultMessage='Success',
            resultCode='SUCCESS'
        )

    @classmethod
    def returnAccessDenied(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='The access is denied.',
            resultCode='ACCESS_DENIED'
        )

    @classmethod
    def returnBusinessNotSupport(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='The payment business is not supported.',
            resultCode='BUSINESS_NOT_SUPPORT'
        )

    @classmethod
    def returnCurrencyNotSupport(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='The currency is not supported.',
            resultCode='CURRENCY_NOT_SUPPORT'
        )

    @classmethod
    def returnExpiredCode(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='The code is expired.',
            resultCode='EXPIRED_CODE'
        )

    @classmethod
    def returnInvalidClient(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='The client is invalid.',
            resultCode='INVALID_CLIENT'
        )

    @classmethod
    def returnInvalidCode(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='The code is invalid.',
            resultCode='INVALID_CODE'
        )

    @classmethod
    def returnInvalidContract(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='The contract is invalid.',
            resultCode='INVALID_CONTRACT'
        )

    @classmethod
    def returnInvalidSignature(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='The signature is invalid.',
            resultCode='INVALID_SIGNATURE'
        )

    @classmethod
    def returnInvalidToken(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='The access token is invalid.',
            resultCode='INVALID_TOKEN'
        )

    @classmethod
    def returnKeyNotFound(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='The key is not found.',
            resultCode='KEY_NOT_FOUND'
        )

    @classmethod
    def returnMediaTypeNotAcceptable(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='The server does not implement the media type that is acceptable to the client.',
            resultCode='MEDIA_TYPE_NOT_ACCEPTABLE'
        )

    @classmethod
    def returnMerchantNotRegistered(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='The merchant is not registered.',
            resultCode='MERCHANT_NOT_REGISTERED'
        )

    @classmethod
    def returnMethodNotSupported(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='The server does not implement the requested HTTP method.',
            resultCode='METHOD_NOT_SUPPORTED'
        )

    @classmethod
    def returnNoInterfaceDef(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='API is not defined.',
            resultCode='NO_INTERFACE_DEF'
        )

    @classmethod
    def returnOrderIsClosed(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='The order is closed.',
            resultCode='ORDER_IS_CLOSED'
        )

    @classmethod
    def returnParamIllegal(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='Illegal parameters exist. For example, a non-numeric input, or an invalid date.',
            resultCode='PARAM_ILLEGAL'
        )

    @classmethod
    def returnPaymentAmountExceedLimit(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='The payment amount exceeds the limit.',
            resultCode='PAYMENT_AMOUNT_EXCEED_LIMIT'
        )

    @classmethod
    def returnPaymentCountExceedLimit(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='The number of payments exceeds the limit.',
            resultCode='PAYMENT_COUNT_EXCEED_LIMIT'
        )

    @classmethod
    def returnProcessFail(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='A general business failure occurred. Don\'t retry.',
            resultCode='PROCESS_FAIL'
        )

    @classmethod
    def returnRegulationRestriction(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='The payment failed due to regulatory restriction.',
            resultCode='REGULATION_RESTRICTION'
        )

    @classmethod
    def returnRepeatReqInconsistent(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='Repeated requests are inconsistent.',
            resultCode='REPEAT_REQ_INCONSISTENT'
        )

    @classmethod
    def returnRiskReject(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='The request is rejected because of the risk control.',
            resultCode='RISK_REJECT'
        )

    @classmethod
    def returnUnavailablePaymentMethod(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='The payment method is unavailable.',
            resultCode='UNAVAILABLE_PAYMENT_METHOD'
        )

    @classmethod
    def returnUserAmountExceedLimit(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='The payment amount exceeds the user payment limit.',
            resultCode='USER_AMOUNT_EXCEED_LIMIT'
        )

    @classmethod
    def returnUserBalanceNotEnough(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='The user balance is not enough for the payment.',
            resultCode='USER_BALANCE_NOT_ENOUGH'
        )

    @classmethod
    def returnUserKycNotQualified(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='The user is not KYC compliant.',
            resultCode='USER_KYC_NOT_QUALIFIED'
        )

    @classmethod
    def returnUserNotExist(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='The user does not exist.',
            resultCode='USER_NOT_EXIST'
        )

    @classmethod
    def returnUserPaymentVerificationFailed(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='User fails to pass the payment verification in the methods like OTP, PIN, and so on.',
            resultCode='USER_PAYMENT_VERIFICATION_FAILED'
        )

    @classmethod
    def returnUserStatusAbnormal(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='The user status is abnormal.',
            resultCode='USER_STATUS_ABNORMAL'
        )

    @classmethod
    def returnPaymentInProcess(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.UNKNOWN,
            resultMessage='The payment is being processed.',
            resultCode='PAYMENT_IN_PROCESS'
        )

    @classmethod
    def returnRequestTrafficExceedLimit(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.UNKNOWN,
            resultMessage='The request traffic exceeds the limit.',
            resultCode='REQUEST_TRAFFIC_EXCEED_LIMIT'
        )

    @classmethod
    def returnUnknownException(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.UNKNOWN,
            resultMessage='An API calling is failed, which is caused by unknown reasons.',
            resultCode='UNKNOWN_EXCEPTION'
        )

    @classmethod
    def returnCancelWindowExceed(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='Exceed Cancel window.',
            resultCode='CANCEL_WINDOW_EXCEED'
        )

    @classmethod
    def returnRefundAmountExceed(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='The total refund amount exceeds the original payment amount.',
            resultCode='REFUND_AMOUNT_EXCEED'
        )

    @classmethod
    def returnRefundWindowExceed(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='The refund request is outside the allowable refund window.',
            resultCode='REFUND_WINDOW_EXCEED'
        )

    @classmethod
    def returnOrderNotExist(cls) -> 'Result':
        return cls(
            resultStatus=ResultStatus.FAILURE,
            resultMessage='The order doesn\'t exist.',
            resultCode='ORDER_NOT_EXIST'
        )


# Retry intervals for PAYMENT_IN_PROCESS (in seconds)
PAYMENT_IN_PROCESS_RETRY_INTERVALS = [2, 2, 3, 3, 5, 5, 10, 10, 10, 10]

# Default payment expiry time in minutes
DEFAULT_PAYMENT_EXPIRY_MINUTES = 1

# Cancel payment retry settings
CANCEL_RETRY_INTERVAL_SECONDS = 10
CANCEL_RETRY_TIMEOUT_SECONDS = 60

# Inquiry payment retry settings
INQUIRY_RETRY_INTERVAL_SECONDS = 5
INQUIRY_RETRY_TIMEOUT_SECONDS = 60

# Allowed User-Agent strings for Entry Code payment
ALIPAY_IOS_USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/18D52 Ariver/1.1.0 AliApp(AP/10.2.15.6000) Nebula WK RVKType(1) AlipayDefined(nt:4G,ws:414|672|3.0) AlipayClient/10.2.15.6000 Alipay Language/zh-Hans Region/CN NebulaX/1.0.0"

ALIPAY_ANDROID_USER_AGENT = "Mozilla/5.0 (Linux; Android 10; Mi 10 Build/QKQ1.191117.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.99 Mobile Safari/537.36 Ariver/2.16.0  Griver/2.16.2 AppContainer/10.5.10 AlipayConnect iapconnectsdk/2.7.0"

# UA Identifiers to check in User-Agent header
ALLOWED_UA_IDENTIFIERS = ['AlipayClient', 'AlipayConnect']
