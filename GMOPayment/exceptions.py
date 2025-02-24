import requests
from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    NotAuthenticated,
    NotFound,
    PermissionDenied,
    ValidationError,
)

class GMOAPIException(APIException):
    """Base exception for GMO API errors"""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'An error occurred while processing the GMO API request.'
    default_code = 'gmo_api_error'

    def __init__(self, detail=None, code=None, response: requests.Response | None = None):
        super().__init__(detail, code)
        self.response = response


class GMOConfigurationError(GMOAPIException):
    """Raised when GMO configuration is invalid"""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'GMO Payment Gateway is not properly configured.'
    default_code = 'gmo_configuration_error'


class GMOAuthenticationError(AuthenticationFailed):
    """Raised when authentication with GMO API fails"""

    default_detail = 'Failed to authenticate with GMO Payment Gateway.'
    default_code = 'gmo_authentication_failed'


class GMONotAuthenticated(NotAuthenticated):
    """Raised when no authentication credentials are provided"""

    default_detail = 'Authentication credentials for GMO Payment Gateway were not provided.'
    default_code = 'gmo_not_authenticated'


class GMOPermissionDenied(PermissionDenied):
    """Raised when the request is not permitted"""

    default_detail = 'You do not have permission to perform this action with GMO Payment Gateway.'
    default_code = 'gmo_permission_denied'


class GMOValidationError(ValidationError):
    """Raised when request validation fails"""

    default_detail = 'Invalid data provided for GMO Payment Gateway request.'
    default_code = 'gmo_validation_error'


class GMONotFound(NotFound):
    """Raised when a resource is not found"""

    default_detail = 'The requested GMO Payment Gateway resource was not found.'
    default_code = 'gmo_not_found'
