"""
Constants and Enums for SuperPayACQP
"""
from enum import Enum
from typing import Optional


class ResultStatus(str, Enum):
    """Result status enumeration"""
    SUCCESS = 'S'
    FAILURE = 'F'
    UNKNOWN = 'U'


class MessageType(str, Enum):
    """API record message type enumeration"""
    INBOUND = 'INBOUND'
    OUTBOUND = 'OUTBOUND'


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


class Result:
    """Result class for API responses"""

    def __init__(
        self,
        resultStatus: Optional[ResultStatus] = None,
        resultMessage: Optional[str] = None,
        resultCode: Optional[str] = None
    ):
        self.resultCode = resultCode
        self.resultStatus = resultStatus
        self.resultMessage = resultMessage

    @classmethod
    def returnSuccess(cls) -> 'Result':
        result = cls()
        result.resultCode = 'SUCCESS'
        result.resultStatus = ResultStatus.SUCCESS
        result.resultMessage = 'Success'
        return result

    @classmethod
    def returnAccessDenied(cls) -> 'Result':
        result = cls()
        result.resultCode = 'ACCESS_DENIED'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'The access is denied.'
        return result

    @classmethod
    def returnBusinessNotSupport(cls) -> 'Result':
        result = cls()
        result.resultCode = 'BUSINESS_NOT_SUPPORT'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'The payment business is not supported.'
        return result

    @classmethod
    def returnCurrencyNotSupport(cls) -> 'Result':
        result = cls()
        result.resultCode = 'CURRENCY_NOT_SUPPORT'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'The currency is not supported.'
        return result

    @classmethod
    def returnExpiredCode(cls) -> 'Result':
        result = cls()
        result.resultCode = 'EXPIRED_CODE'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'The code is expired.'
        return result

    @classmethod
    def returnInvalidClient(cls) -> 'Result':
        result = cls()
        result.resultCode = 'INVALID_CLIENT'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'The client is invalid.'
        return result

    @classmethod
    def returnInvalidCode(cls) -> 'Result':
        result = cls()
        result.resultCode = 'INVALID_CODE'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'The code is invalid.'
        return result

    @classmethod
    def returnInvalidContract(cls) -> 'Result':
        result = cls()
        result.resultCode = 'INVALID_CONTRACT'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'The contract is invalid.'
        return result

    @classmethod
    def returnInvalidSignature(cls) -> 'Result':
        result = cls()
        result.resultCode = 'INVALID_SIGNATURE'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'The signature is invalid.'
        return result

    @classmethod
    def returnInvalidToken(cls) -> 'Result':
        result = cls()
        result.resultCode = 'INVALID_TOKEN'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'The access token is invalid.'
        return result

    @classmethod
    def returnKeyNotFound(cls) -> 'Result':
        result = cls()
        result.resultCode = 'KEY_NOT_FOUND'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'The key is not found.'
        return result

    @classmethod
    def returnMediaTypeNotAcceptable(cls) -> 'Result':
        result = cls()
        result.resultCode = 'MEDIA_TYPE_NOT_ACCEPTABLE'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'The server does not implement the media type that is acceptable to the client.'
        return result

    @classmethod
    def returnMerchantNotRegistered(cls) -> 'Result':
        result = cls()
        result.resultCode = 'MERCHANT_NOT_REGISTERED'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'The merchant is not registered.'
        return result

    @classmethod
    def returnMethodNotSupported(cls) -> 'Result':
        result = cls()
        result.resultCode = 'METHOD_NOT_SUPPORTED'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'The server does not implement the requested HTTP method.'
        return result

    @classmethod
    def returnNoInterfaceDef(cls) -> 'Result':
        result = cls()
        result.resultCode = 'NO_INTERFACE_DEF'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'API is not defined.'
        return result

    @classmethod
    def returnOrderIsClosed(cls) -> 'Result':
        result = cls()
        result.resultCode = 'ORDER_IS_CLOSED'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'The order is closed.'
        return result

    @classmethod
    def returnParamIllegal(cls) -> 'Result':
        result = cls()
        result.resultCode = 'PARAM_ILLEGAL'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'Illegal parameters exist. For example, a non-numeric input, or an invalid date.'
        return result

    @classmethod
    def returnPaymentAmountExceedLimit(cls) -> 'Result':
        result = cls()
        result.resultCode = 'PAYMENT_AMOUNT_EXCEED_LIMIT'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'The payment amount exceeds the limit.'
        return result

    @classmethod
    def returnPaymentCountExceedLimit(cls) -> 'Result':
        result = cls()
        result.resultCode = 'PAYMENT_COUNT_EXCEED_LIMIT'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'The number of payments exceeds the limit.'
        return result

    @classmethod
    def returnProcessFail(cls) -> 'Result':
        result = cls()
        result.resultCode = 'PROCESS_FAIL'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'A general business failure occurred. Don\'t retry.'
        return result

    @classmethod
    def returnRegulationRestriction(cls) -> 'Result':
        result = cls()
        result.resultCode = 'REGULATION_RESTRICTION'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'The payment failed due to regulatory restriction.'
        return result

    @classmethod
    def returnRepeatReqInconsistent(cls) -> 'Result':
        result = cls()
        result.resultCode = 'REPEAT_REQ_INCONSISTENT'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'Repeated requests are inconsistent.'
        return result

    @classmethod
    def returnRiskReject(cls) -> 'Result':
        result = cls()
        result.resultCode = 'RISK_REJECT'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'The request is rejected because of the risk control.'
        return result

    @classmethod
    def returnUnavailablePaymentMethod(cls) -> 'Result':
        result = cls()
        result.resultCode = 'UNAVAILABLE_PAYMENT_METHOD'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'The payment method is unavailable.'
        return result

    @classmethod
    def returnUserAmountExceedLimit(cls) -> 'Result':
        result = cls()
        result.resultCode = 'USER_AMOUNT_EXCEED_LIMIT'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'The payment amount exceeds the user payment limit.'
        return result

    @classmethod
    def returnUserBalanceNotEnough(cls) -> 'Result':
        result = cls()
        result.resultCode = 'USER_BALANCE_NOT_ENOUGH'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'The user balance is not enough for the payment.'
        return result

    @classmethod
    def returnUserKycNotQualified(cls) -> 'Result':
        result = cls()
        result.resultCode = 'USER_KYC_NOT_QUALIFIED'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'The user is not KYC compliant.'
        return result

    @classmethod
    def returnUserNotExist(cls) -> 'Result':
        result = cls()
        result.resultCode = 'USER_NOT_EXIST'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'The user does not exist.'
        return result

    @classmethod
    def returnUserPaymentVerificationFailed(cls) -> 'Result':
        result = cls()
        result.resultCode = 'USER_PAYMENT_VERIFICATION_FAILED'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'User fails to pass the payment verification in the methods like OTP, PIN, and so on.'
        return result

    @classmethod
    def returnUserStatusAbnormal(cls) -> 'Result':
        result = cls()
        result.resultCode = 'USER_STATUS_ABNORMAL'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'The user status is abnormal.'
        return result

    @classmethod
    def returnPaymentInProcess(cls) -> 'Result':
        result = cls()
        result.resultCode = 'PAYMENT_IN_PROCESS'
        result.resultStatus = ResultStatus.UNKNOWN
        result.resultMessage = 'The payment is being processed.'
        return result

    @classmethod
    def returnRequestTrafficExceedLimit(cls) -> 'Result':
        result = cls()
        result.resultCode = 'REQUEST_TRAFFIC_EXCEED_LIMIT'
        result.resultStatus = ResultStatus.UNKNOWN
        result.resultMessage = 'The request traffic exceeds the limit.'
        return result

    @classmethod
    def returnUnknownException(cls) -> 'Result':
        result = cls()
        result.resultCode = 'UNKNOWN_EXCEPTION'
        result.resultStatus = ResultStatus.UNKNOWN
        result.resultMessage = 'An API calling is failed, which is caused by unknown reasons.'
        return result

    @classmethod
    def returnCancelWindowExceed(cls) -> 'Result':
        result = cls()
        result.resultCode = 'CANCEL_WINDOW_EXCEED'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'Exceed Cancel window.'
        return result

    @classmethod
    def returnRefundAmountExceed(cls) -> 'Result':
        result = cls()
        result.resultCode = 'REFUND_AMOUNT_EXCEED'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'The total refund amount exceeds the original payment amount.'
        return result

    @classmethod
    def returnRefundWindowExceed(cls) -> 'Result':
        result = cls()
        result.resultCode = 'REFUND_WINDOW_EXCEED'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'The refund request is outside the allowable refund window.'
        return result

    @classmethod
    def returnOrderNotExist(cls) -> 'Result':
        result = cls()
        result.resultCode = 'ORDER_NOT_EXIST'
        result.resultStatus = ResultStatus.FAILURE
        result.resultMessage = 'The order doesn\'t exist.'
        return result


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
