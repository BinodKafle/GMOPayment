import base64
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import Any, TypeVar, cast
from urllib.parse import urljoin

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from rest_framework import status

from requests.adapters import HTTPAdapter
import requests
from urllib3 import Retry

from GMOPayment.exceptions import GMONotAuthenticated, GMOValidationError, GMOPermissionDenied, GMONotFound, \
    GMOConfigurationError, GMOAPIException, GMOAuthenticationError

T = TypeVar('T', bound=Callable[..., Any])


class GMOEnvironment(str, Enum):
    """Environment options for GMO API"""

    PRODUCTION = 'production'
    TEST = 'test'

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class GMOCredentials:
    """Immutable credentials for GMO API"""

    shop_id: str
    shop_password: str
    site_id: str
    site_password: str


@dataclass(frozen=True, slots=True)
class GMOUrls:
    """Immutable URLs for GMO API"""

    api_base_url: str
    oauth_url: str
    payment_method_token_url: str



def require_auth(func: T) -> T:
    """Decorator to ensure authentication before making requests"""
    @wraps(func)
    def wrapper(self: 'GMOHttpClient', *args: Any, **kwargs: Any) -> Any:
        if not self._access_token:
            raise GMONotAuthenticated()
        return func(self, *args, **kwargs)
    return cast(T, wrapper)


class GMOHttpClient:
    """HTTP client for GMO Payment Gateway API"""

    ERROR_STATUS_MAP = {
        status.HTTP_400_BAD_REQUEST: GMOValidationError,
        status.HTTP_401_UNAUTHORIZED: GMONotAuthenticated,
        status.HTTP_403_FORBIDDEN: GMOPermissionDenied,
        status.HTTP_404_NOT_FOUND: GMONotFound,
        status.HTTP_422_UNPROCESSABLE_ENTITY: GMOValidationError,
    }

    def __init__(
            self,
            credentials: GMOCredentials | None = None,
            environment: GMOEnvironment = GMOEnvironment.TEST,
            timeout: int = 30,
            max_retries: int = 3
    ):
        """Initialize GMO HTTP client"""
        try:
            self.credentials = credentials or self._load_credentials_from_settings()
            self.environment = environment
            self.timeout = timeout
            self.urls = self._get_environment_urls()
            self.session = self._configure_session(max_retries)
            self._access_token: str | None = None
        except ImproperlyConfigured as e:
            raise GMOConfigurationError(str(e))

    @staticmethod
    def _load_credentials_from_settings() -> GMOCredentials:
        """Load GMO credentials from Django settings"""
        try:
            gmo_settings = settings.GMO_PAYMENT
            return GMOCredentials(
                shop_id=gmo_settings['shop_id'],
                shop_password=gmo_settings['shop_password'],
                site_id=gmo_settings['site_id'],
                site_password=gmo_settings['site_password']
            )
        except (AttributeError, KeyError) as e:
            raise ImproperlyConfigured(f"Missing GMO Payment configuration: {e!s}")

    def _get_environment_urls(self) -> GMOUrls:
        """Get API URLs based on environment"""
        try:
            gmo_settings = settings.GMO_PAYMENT
            if self.environment == GMOEnvironment.PRODUCTION:
                return GMOUrls(
                    api_base_url=gmo_settings['prod_api_url'],
                    oauth_url=gmo_settings['prod_oauth_url'],
                    payment_method_token_url=gmo_settings['prod_payment_method_token_url']
                )
            return GMOUrls(
                api_base_url=gmo_settings['test_api_url'],
                oauth_url=gmo_settings['test_oauth_url'],
                payment_method_token_url=gmo_settings['test_payment_method_token_url'],
            )
        except (AttributeError, KeyError) as e:
            raise ImproperlyConfigured(f"Missing GMO Payment URLs: {e!s}")

    def _configure_session(self, max_retries: int) -> requests.Session:
        """Configure requests session with retry logic"""
        session = requests.Session()

        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

        return session

    @property
    def _token_cache_key(self) -> str:
        """Get cache key for access token"""
        return f"gmo_token_{self.credentials.shop_id}_{self.environment}"


    def _handle_error_response(self, response: requests.Response) -> None:
        """Handle error responses from GMO API"""
        try:
            error_data = response.json()
        except ValueError:
            error_data = None

        if isinstance(error_data, dict):
            detail = {
                "code": str(error_data.get("title", "error")),
                "detail": str(error_data.get("message") or error_data.get("error") or response.text),
                "instance": str(error_data.get("instance", response.url)),
            }
        else:
            detail = {"detail": str(response.text)}

        exceptions = self.ERROR_STATUS_MAP.get(response.status_code, GMOAPIException)
        raise exceptions(detail)


    def authenticate(self) -> None:
        """Authenticate with GMO API"""
        if cached_token := cache.get(self._token_cache_key):
            self._access_token = cached_token
            self.session.headers["Authorization"] = f"Bearer {cached_token}"
            return

        try:
            auth_string = f"{self.credentials.shop_id}:{self.credentials.shop_password}"
            encoded_auth = base64.b64encode(auth_string.encode()).decode()

            response = self.session.post(
                self.urls.oauth_url,
                headers={
                    "Authorization": f"Basic {encoded_auth}",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                data={
                    "grant_type": "client_credentials",
                    "scope": "openapi"
                },
                timeout=self.timeout
            )

            if not response.ok:
                raise GMOAuthenticationError(
                    f"Authentication failed: {response.text}"
                )

            token_data = response.json()
            if not (access_token := token_data.get("access_token")):
                raise GMOAuthenticationError("No access token in response")

            cache.set(self._token_cache_key, access_token, timeout=3600)
            self._access_token = access_token
            self.session.headers["Authorization"] = f"Bearer {access_token}"

        except requests.RequestException as e:
            raise GMOAuthenticationError(f"Authentication request failed: {e!s}")

    def request(
            self,
            method: str,
            endpoint: str,
            params: dict[str, Any] | None = None,
            json_data: dict[str, Any] | None = None,
            **kwargs: Any
    ) -> dict[str, Any]:
        """Make an authenticated request to the GMO API"""
        # Check for cached token first
        if cached_token := cache.get(self._token_cache_key):
            self._access_token = cached_token
            self.session.headers["Authorization"] = f"Bearer {cached_token}"
        elif not self._access_token:
            self.authenticate()

        try:
            url = urljoin(self.urls.api_base_url, endpoint)

            response = self.session.request(
                method=method.upper(),
                url=url,
                params=params,
                json=json_data,
                timeout=self.timeout,
                **kwargs
            )

            if response.status_code == status.HTTP_401_UNAUTHORIZED:
                cache.delete(self._token_cache_key)
                self.authenticate()
                return self.request(method, endpoint, params, json_data, **kwargs)

            if not response.ok:
                self._handle_error_response(response)

            return response.json()

        except requests.Timeout:
            raise GMOAPIException(
                detail=f"Request timed out after {self.timeout}s",
                code='request_timeout'
            )
        except requests.RequestException as e:
            raise GMOAPIException(
                detail=f"Request failed: {e!s}",
                code='request_error'
            )

    # Convenience methods for common HTTP methods
    def get(self, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """Send GET request"""
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, data: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        """Send POST request"""
        return self.request("POST", endpoint, json_data=data, **kwargs)

    def put(self, endpoint: str, data: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        """Send PUT request"""
        return self.request("PUT", endpoint, json_data=data, **kwargs)

    def delete(self, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """Send DELETE request"""
        return self.request("DELETE", endpoint, **kwargs)
