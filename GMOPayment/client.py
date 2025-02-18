import base64
import uuid
from dataclasses import dataclass
from urllib.parse import parse_qsl

import requests
import logging
from typing import Dict, Any, Optional
from django.conf import settings

from GMOPayment.exceptions import GMOValidationError, GMOAPIError, GMOConnectionError

logger = logging.getLogger(__name__)


@dataclass
class GMOConfig:
    """Configuration for GMO Payment Gateway."""
    shop_id: str
    shop_password: str
    site_id: str
    site_password: str
    prod_api_url: str
    test_api_url: str
    prod_oauth_url: str
    test_oauth_url: str
    is_production: bool = False
    timeout: int = 30  # Timeout in seconds

    def __post_init__(self) -> None:
        if self.is_production:
            self.oauth_url = self.prod_oauth_url
            self.api_url = self.prod_api_url  # Production environment
            logger.info("Using GMO production environment")
        else:
            self.oauth_url = self.test_oauth_url  # Test environment
            self.api_url = self.test_api_url
            logger.info("Using GMO test environment")

        if not self.shop_id or not self.shop_password:
            raise GMOValidationError("Shop ID and Shop Password are required")


class GMOClient:
    """Client for interacting with GMO Payment Gateway API."""

    def __init__(self, config: GMOConfig):
        self.config = config
        self.session = requests.Session()
        self.access_token = None
        self._get_access_token()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })

    def _get_access_token(self) -> None:
        endpoint = f"{self.config.oauth_url}"

        credentials = f"{self.config.shop_id}:{self.config.shop_password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        payload = {
            "grant_type": "client_credentials",
            "scope": "openapi",
        }

        try:
            response = self.session.post(endpoint, data=payload, headers=headers, timeout=30)
            logger.debug(f"OAuth Response: {response.status_code} - {response.text}")
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data.get("access_token")
            if not self.access_token:
                raise GMOAPIError("Failed to retrieve access token")

            # Set Authorization Header for subsequent requests
            self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
            logger.info("Successfully obtained GMO access token")

        except requests.RequestException as e:
            logger.error(f"Failed to get GMO access token: {e.response.text if e.response else str(e)}", exc_info=True)
            raise GMOConnectionError(f"Failed to obtain access token: {str(e)}") from e


    def _make_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to the GMO API."""
        url = f"{self.config.api_url}/{endpoint}"
        request_id = str(uuid.uuid4())[:8]

        # Log the request
        self._log_request(request_id, endpoint, params, payload)

        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params, timeout=self.config.timeout)
            elif method.upper() == "POST":
                response = self.session.post(url, data=payload, timeout=self.config.timeout)
            else:
                raise ValueError("Invalid request method")

            # Log response status
            logger.debug(f"[{request_id}] GMO Response status: {response.status_code}")

            # Check for HTTP errors
            response.raise_for_status()

            # Parse the response
            response_dict = self._parse_response(response.text)

            # Log the response
            self._log_response(request_id, response, response_dict)

            # If the token expired, refresh it and retry
            if response.status_code == 401:
                logger.warning("Access token expired, refreshing token...")
                self._get_access_token()
                return self._make_request(method, endpoint, params, payload)

            # Check for API errors
            if "ErrCode" in response_dict or "errCode" in response_dict:
                error_code = response_dict.get("ErrCode") or response_dict.get("errCode")
                error_info = response_dict.get("ErrInfo") or response_dict.get("errInfo", "Unknown error")
                raise GMOAPIError(f"GMO API Error: {error_info}", error_code=error_code, response=response_dict)

            return response_dict

        except requests.RequestException as e:
            logger.error(f"[{request_id}] Request failed: {str(e)}")
            if isinstance(e, requests.Timeout):
                raise GMOConnectionError(f"Request timed out after {self.config.timeout}s") from e
            else:
                raise GMOConnectionError(f"Connection error: {str(e)}") from e


    @staticmethod
    def _parse_response(response_text: str) -> Dict[str, str]:
        """Parse GMO response from URL-encoded format to dictionary."""
        if not response_text:
            logger.warning("Empty response received from GMO API")
            return {}

        try:
            # Use parse_qsl for safer parsing
            return dict(parse_qsl(response_text))
        except Exception as e:
            logger.error(f"Failed to parse response: {response_text}")
            raise GMOAPIError(f"Failed to parse response: {str(e)}")

    @staticmethod
    def _mask_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive data for logging."""
        sensitive_keys = ['ShopPass', 'SitePass', 'CardNo', 'SecurityCode', 'Access']
        masked_data = data.copy()

        for key in masked_data:
            for sensitive_key in sensitive_keys:
                if sensitive_key in key:
                    if isinstance(masked_data[key], str) and len(masked_data[key]) > 4:
                        # Keep last 4 chars for debugging, mask the rest
                        masked_data[key] = '****' + masked_data[key][-4:]
                    else:
                        masked_data[key] = '****'

        return masked_data

    def _log_request(self, request_id: str, endpoint: str, params: Dict[str, Any] = None, payload: Dict[str, Any] = None) -> None:
        """Log the request details, masking sensitive information."""
        masked_params = self._mask_sensitive_data(params.copy()) if params else None
        masked_payload = self._mask_sensitive_data(payload.copy()) if payload else None
        if masked_params:
            logger.debug(f"[{request_id}] GMO Request to {endpoint} - Params: {masked_params}")
        if masked_payload:
            logger.debug(f"[{request_id}] GMO Request to {endpoint} - Payload: {masked_payload}")

    def _log_response(self, request_id: str, response: requests.Response, response_dict: Dict[str, Any]) -> None:
        """Log the response details, masking sensitive information."""
        logger.debug(f"[{request_id}] GMO Response status: {response.status_code}")
        masked_response = self._mask_sensitive_data(response_dict.copy())
        logger.debug(f"[{request_id}] GMO Response: {masked_response}")

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._make_request("GET", endpoint, params=params)

    def post(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", endpoint, payload=payload)




def get_client(config: Optional[Dict[str, Any]] = None) -> GMOClient:
    """Get a configured GMO client from Django settings."""
    if config is None:
        config = getattr(settings, 'GMO_PAYMENT', {})
    return GMOClient(GMOConfig(**config))
