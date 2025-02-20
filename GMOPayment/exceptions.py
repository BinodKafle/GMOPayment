from typing import Optional, Dict, Any

class GMOErrorCode:
    """GMO error codes for better error handling and structured error messages."""

    # Standard GMO error codes
    INVALID_SHOP_ID = "E01"
    INVALID_SHOP_PASSWORD = "E02"
    INVALID_CARD_NUMBER = "E41"
    EXPIRED_CARD = "E42"
    SECURITY_CODE_MISSING = "E44"
    CARD_REJECTED = "G12"
    TRANSACTION_NOT_FOUND = "G30"

    # Error message mapping
    MESSAGES = {
        INVALID_SHOP_ID: "Invalid shop ID provided",
        INVALID_SHOP_PASSWORD: "Invalid shop password provided",
        INVALID_CARD_NUMBER: "Invalid card number provided",
        EXPIRED_CARD: "The card has expired",
        SECURITY_CODE_MISSING: "Security code is required but missing",
        CARD_REJECTED: "The card was rejected by the payment processor",
        TRANSACTION_NOT_FOUND: "Transaction not found",
    }

    @classmethod
    def get_message(cls, code: str) -> str:
        """Return a human-readable message for a given error code."""
        return cls.MESSAGES.get(code, f"Unknown error (code: {code})")


class GMOAPIError(Exception):
    """Exception for GMO API errors with detailed error messages and response logging."""

    def __init__(self, message: str, error_code: Optional[str] = None, response: Optional[Dict[str, Any]] = None):
        self.error_code = error_code
        self.response = response

        # Append the detailed error message if the error code is recognized
        detailed_message = GMOErrorCode.get_message(error_code) if error_code else None
        self.message = f"{message} - {detailed_message}" if detailed_message else message

        super().__init__(self.message)

    def __str__(self):
        """Return a readable error message with debugging details."""
        base_message = f"GMOAPIError: {self.message}"
        if self.error_code:
            base_message += f" (Error Code: {self.error_code})"
        if self.response:
            base_message += f" | Response: {self.response}"
        return base_message


class GMOConnectionError(Exception):
    """Exception for network/connection errors with GMO API."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        """Return a readable error message."""
        return f"GMOConnectionError: {self.message}"


class GMOValidationError(Exception):
    """Exception for validation errors in requests to GMO API."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        """Return a readable error message."""
        return f"GMOValidationError: {self.message}"
