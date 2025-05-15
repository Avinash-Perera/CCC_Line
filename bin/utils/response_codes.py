from enum import Enum

class PaymentResponseCode(str, Enum):
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"
    EXPIRED_CARD = "EXPIRED_CARD"
    INSUFFICIENT_FUNDS = "INSUFFICIENT_FUNDS"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    INVALID_CSC = "INVALID_CSC"
    NOT_ENROLLED_3D_SECURE = "NOT_ENROLLED_3D_SECURE"
    DECLINED_AVS = "DECLINED_AVS"
    TIMED_OUT = "TIMED_OUT"
    SYSTEM_ERROR = "SYSTEM_ERROR"
    DUPLICATE_BATCH = "DUPLICATE_BATCH"
    PENDING = "PENDING"
    REFERRED = "REFERRED"
    ABORTED = "ABORTED"
    CANCELLED = "CANCELLED"

class PaymentStatus(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING = "pending"
    CANCELLED = "cancelled"

def get_error_message(gateway_code: PaymentResponseCode) -> str:
    error_mapping = {
        PaymentResponseCode.DECLINED: "Transaction was declined by the bank",
        PaymentResponseCode.EXPIRED_CARD: "The card used has expired",
        PaymentResponseCode.INSUFFICIENT_FUNDS: "Insufficient funds in the account",
        PaymentResponseCode.SYSTEM_ERROR: "Internal payment processing error",
        PaymentResponseCode.AUTHENTICATION_FAILED: "3D Secure authentication failed",
        PaymentResponseCode.INVALID_CSC: "Invalid card security code",
        PaymentResponseCode.NOT_ENROLLED_3D_SECURE: "Card not enrolled in 3D Secure",
        PaymentResponseCode.DECLINED_AVS: "Address verification failed",
        PaymentResponseCode.TIMED_OUT: "Transaction timed out, please try again",
        PaymentResponseCode.DUPLICATE_BATCH: "Duplicate transaction detected",
        PaymentResponseCode.REFERRED: "Transaction requires special approval",
        PaymentResponseCode.ABORTED: "Transaction was aborted by user",
        PaymentResponseCode.CANCELLED: "Transaction was cancelled",
    }
    return error_mapping.get(gateway_code, "Payment processing failed")

def is_retryable_error(gateway_code: PaymentResponseCode) -> bool:
    return gateway_code in [
        PaymentResponseCode.TIMED_OUT,
        PaymentResponseCode.SYSTEM_ERROR
    ]