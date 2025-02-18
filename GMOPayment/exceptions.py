from typing import Optional, Dict, Any


class GMOErrorCode:
    """GMO error codes for better error handling."""

    INVALID_SHOP_ID = "E01"
    INVALID_SHOP_PASSWORD = "E02"
    INVALID_CARD_NUMBER = "E41"
    EXPIRED_CARD = "E42"
    SECURITY_CODE_MISSING = "E44"
    CARD_REJECTED = "G12"
    TRANSACTION_NOT_FOUND = "G30"

    @classmethod
    def get_message(cls, code: str) -> str:
        """Return a human-readable message for an error code."""
        messages = {
            cls.INVALID_SHOP_ID: "Invalid shop ID provided",
            cls.INVALID_SHOP_PASSWORD: "Invalid shop password provided",
            cls.INVALID_CARD_NUMBER: "Invalid card number provided",
            cls.EXPIRED_CARD: "The card has expired",
            cls.SECURITY_CODE_MISSING: "Security code is required but missing",
            cls.CARD_REJECTED: "The card was rejected by the payment processor",
            cls.TRANSACTION_NOT_FOUND: "Transaction not found",
        }
        return messages.get(code, f"Unknown error (code: {code})")


class GMOAPIError(Exception):
    """Exception for GMO API errors."""

    def __init__(self, message: str, error_code: Optional[str] = None, response: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.response = response

        # Use the error code to provide a better error message if available
        if error_code and hasattr(GMOErrorCode, 'get_message'):
            detailed_message = GMOErrorCode.get_message(error_code)
            if detailed_message != f"Unknown error (code: {error_code})":
                self.message = f"{message} - {detailed_message}"

        super().__init__(self.message)


class GMOConnectionError(Exception):
    """Exception for network/connection errors with GMO API."""
    pass


class GMOValidationError(Exception):
    """Exception for validation errors in requests to GMO API."""
    pass
