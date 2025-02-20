import base64
import json
import threading
import uuid
from dataclasses import dataclass, field
from urllib.parse import parse_qsl

import requests
import logging
from typing import Dict, Any, Optional
from django.conf import settings

from GMOPayment.exceptions import GMOValidationError, GMOAPIError, GMOConnectionError

_gmo_client = None
_client_lock = threading.Lock()  # Ensures thread safety

logger = logging.getLogger(__name__)


@dataclass
class GMOConfig:
    """Configuration for GMO Payment Gateway."""
    shop_id: str = field(default_factory=lambda: settings.GMO_PAYMENT.get("shop_id", ""))
    shop_password: str = field(default_factory=lambda: settings.GMO_PAYMENT.get("shop_password", ""))
    site_id: str = field(default_factory=lambda: settings.GMO_PAYMENT.get("site_id", ""))
    site_password: str = field(default_factory=lambda: settings.GMO_PAYMENT.get("site_password", ""))
    prod_api_url: str = field(default_factory=lambda: settings.GMO_PAYMENT.get("prod_api_url", ""))
    test_api_url: str = field(default_factory=lambda: settings.GMO_PAYMENT.get("test_api_url", ""))
    prod_oauth_url: str = field(default_factory=lambda: settings.GMO_PAYMENT.get("prod_oauth_url", ""))
    test_oauth_url: str = field(default_factory=lambda: settings.GMO_PAYMENT.get("test_oauth_url", ""))
    is_production: bool = field(default_factory=lambda: settings.GMO_PAYMENT.get("is_production", False))
    timeout: int = field(default=30)  # Timeout in seconds

    def __post_init__(self) -> None:
        """Ensure valid configuration and set API URLs based on the environment."""
        if not self.shop_id or not self.shop_password:
            raise GMOValidationError("Shop ID and Shop Password are required")
        if not self.site_id or not self.site_password:
            raise GMOValidationError("Site ID and Site Password are required")
        if not self.prod_api_url or not self.test_api_url:
            raise GMOValidationError("Both production and test API URLs must be provided")
        if not self.prod_oauth_url or not self.test_oauth_url:
            raise GMOValidationError("Both production and test OAuth URLs must be provided")

        self.api_url = self.prod_api_url if self.is_production else self.test_api_url
        self.oauth_url = self.prod_oauth_url if self.is_production else self.test_oauth_url

        logger.info(f"Using {'production' if self.is_production else 'test'} GMO environment")


class GMOClient:
    """Client for interacting with GMO Payment Gateway API."""

    def __init__(self, config: Optional[GMOConfig] = None):
        self.config = config or self._load_default_config()
        self.session = requests.Session()
        self.access_token = None
        self._get_access_token()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })

    @staticmethod
    def _load_default_config() -> GMOConfig:
        """Load default config using GMOConfig dataclass."""
        return GMOConfig()

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
            print(self.access_token)
            logger.info("Successfully obtained GMO access token")

        except requests.RequestException as e:
            logger.error(f"Failed to get GMO access token: {e.response.text if e.response else str(e)}", exc_info=True)
            raise GMOConnectionError(f"Failed to obtain access token: {str(e)}") from e

    def _make_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None,
                      payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to the GMO API and handle errors properly."""
        url = f"{self.config.api_url}/{endpoint}"
        request_id = str(uuid.uuid4())[:8]

        # Log the request
        self._log_request(request_id, endpoint, params, payload)

        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params, timeout=self.config.timeout)
            elif method.upper() == "POST":
                response = self.session.post(url, json=payload, timeout=self.config.timeout)
            else:
                raise ValueError("Invalid request method")

            # Check for HTTP errors
            try:
                response.raise_for_status()
            except requests.HTTPError:
                try:
                    error_json = response.json()
                    error_message = error_json.get("message", error_json)
                except (json.JSONDecodeError, AttributeError):
                    error_message = response.text

                logger.error(f"[{request_id}] GMO API returned HTTP error {response.status_code}: {error_message}")
                raise GMOAPIError(f"{response.status_code}: {error_message}")

            # Parse the response
            response_dict = self._parse_response(response.text)

            # Log the response
            self._log_response(request_id, response, response_dict)

            # If the token expired, refresh it and retry
            if response.status_code == 401:
                logger.warning("Access token expired, refreshing token...")
                self._get_access_token()
                return self._make_request(method, endpoint, params, payload)

            return response_dict

        except requests.RequestException as e:
            error_response = getattr(e.response, "text", str(e))
            if isinstance(e, requests.Timeout):
                raise GMOConnectionError(f"Request timed out after {self.config.timeout}s") from e
            else:
                raise GMOConnectionError(f"Connection error: {error_response}") from e


    @staticmethod
    def _parse_response(response_text: str) -> Dict[str, str]:
        """Parse GMO response from URL-encoded format to dictionary."""
        if not response_text:
            logger.warning("Empty response received from GMO API")
            return {}

        try:
            # First, try parsing as JSON
            return json.loads(response_text)
        except json.JSONDecodeError:
            logger.info("Response is not JSON, attempting URL-decoded parsing.")

        try:
            # If JSON parsing fails, fallback to URL-decoded parsing
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


def get_client() -> GMOClient:
    """Returns a singleton instance of GMOClient."""
    global _gmo_client
    if _gmo_client is None:
        with _client_lock:  # Prevents race conditions in multithreaded environments
            if _gmo_client is None:  # Double-check inside the lock
                _gmo_client = GMOClient(GMOConfig())
    return _gmo_client
