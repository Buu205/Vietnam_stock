"""
Base API Client
===============

Abstract base class for all API clients with retry, timeout, and logging.
"""

import time
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional, Any, List

import requests
from requests.exceptions import Timeout, ConnectionError as RequestsConnectionError

from PROCESSORS.api.core.exceptions import (
    APIError,
    APITimeoutError,
    APIConnectionError,
    APIAuthenticationError,
    APIRateLimitError,
    APIResponseError,
)
from PROCESSORS.api.core.retry_handler import RetryHandler, RetryConfig

logger = logging.getLogger(__name__)


@dataclass
class APIResponse:
    """Standardized API response wrapper."""

    success: bool
    data: Optional[Any] = None
    status_code: int = 0
    error_message: Optional[str] = None
    response_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    headers: Dict[str, str] = field(default_factory=dict)

    def __bool__(self):
        return self.success


class BaseAPIClient(ABC):
    """
    Abstract base class for all API clients.

    Features:
    - Configurable retry logic with exponential backoff
    - Request/response logging
    - Health check integration
    - Credential management
    - Session management with connection pooling

    Usage:
        class MyClient(BaseAPIClient):
            def get_headers(self) -> Dict[str, str]:
                return {"Authorization": f"Bearer {self.api_token}"}

            def validate_credentials(self) -> bool:
                return self.api_token is not None

        client = MyClient(name="my_api", base_url="https://api.example.com")
        response = client.get("/endpoint", params={"key": "value"})
    """

    def __init__(
        self,
        name: str,
        base_url: str,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        rate_limit_per_minute: int = 60,
    ):
        """
        Initialize API client.

        Args:
            name: Client name for logging
            base_url: Base URL for API
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            retry_delay: Base delay between retries
            rate_limit_per_minute: Max requests per minute
        """
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.rate_limit_per_minute = rate_limit_per_minute

        # Session for connection pooling
        self._session = requests.Session()

        # Retry handler
        self._retry_handler = RetryHandler(
            RetryConfig(
                max_retries=max_retries,
                base_delay=retry_delay,
            )
        )

        # Metrics tracking
        self._request_count = 0
        self._error_count = 0
        self._total_response_time = 0.0
        self._last_request_time: Optional[datetime] = None

        logger.info(f"[{self.name}] Initialized API client for {self.base_url}")

    @abstractmethod
    def get_headers(self) -> Dict[str, str]:
        """
        Return headers for API requests.

        Must be implemented by subclasses.

        Returns:
            Dict of HTTP headers
        """
        pass

    @abstractmethod
    def validate_credentials(self) -> bool:
        """
        Validate that credentials are configured.

        Must be implemented by subclasses.

        Returns:
            True if credentials are valid, False otherwise
        """
        pass

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Dict = None,
        data: Dict = None,
        json_data: Dict = None,
        extra_headers: Dict = None,
    ) -> APIResponse:
        """
        Make HTTP request with error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (will be appended to base_url)
            params: Query parameters
            data: Form data
            json_data: JSON body data
            extra_headers: Additional headers to merge

        Returns:
            APIResponse object
        """
        url = f"{self.base_url}{endpoint}"
        headers = self.get_headers()
        if extra_headers:
            headers.update(extra_headers)

        start_time = time.time()

        def execute_request():
            try:
                response = self._session.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    json=json_data,
                    headers=headers,
                    timeout=self.timeout,
                )

                response_time = (time.time() - start_time) * 1000

                # Update metrics
                self._request_count += 1
                self._total_response_time += response_time
                self._last_request_time = datetime.now()

                # Check for errors
                if response.status_code == 401:
                    self._error_count += 1
                    raise APIAuthenticationError(self.name)

                if response.status_code == 429:
                    self._error_count += 1
                    retry_after = response.headers.get("Retry-After")
                    raise APIRateLimitError(
                        self.name, int(retry_after) if retry_after else None
                    )

                if response.status_code >= 400:
                    self._error_count += 1
                    raise APIResponseError(
                        self.name, response.status_code, response.text[:500]
                    )

                # Try to parse JSON
                try:
                    response_data = response.json()
                except ValueError:
                    response_data = response.text

                logger.debug(
                    f"[{self.name}] {method} {endpoint} -> {response.status_code} "
                    f"({response_time:.0f}ms)"
                )

                return APIResponse(
                    success=True,
                    data=response_data,
                    status_code=response.status_code,
                    response_time_ms=response_time,
                    headers=dict(response.headers),
                )

            except Timeout as e:
                self._error_count += 1
                raise APITimeoutError(self.name, self.timeout, endpoint)

            except RequestsConnectionError as e:
                self._error_count += 1
                raise APIConnectionError(self.name, url, e)

        # Execute with retry
        return self._retry_handler.execute_with_retry(
            execute_request, api_name=self.name, endpoint=endpoint
        )

    def get(
        self,
        endpoint: str,
        params: Dict = None,
        extra_headers: Dict = None,
    ) -> APIResponse:
        """
        Make GET request.

        Args:
            endpoint: API endpoint
            params: Query parameters
            extra_headers: Additional headers

        Returns:
            APIResponse object
        """
        return self._make_request(
            "GET", endpoint, params=params, extra_headers=extra_headers
        )

    def post(
        self,
        endpoint: str,
        data: Dict = None,
        json_data: Dict = None,
        extra_headers: Dict = None,
    ) -> APIResponse:
        """
        Make POST request.

        Args:
            endpoint: API endpoint
            data: Form data
            json_data: JSON body
            extra_headers: Additional headers

        Returns:
            APIResponse object
        """
        return self._make_request(
            "POST",
            endpoint,
            data=data,
            json_data=json_data,
            extra_headers=extra_headers,
        )

    def health_check(self) -> bool:
        """
        Check if API is healthy.

        Override in subclass for specific health check logic.

        Returns:
            True if API is healthy, False otherwise
        """
        try:
            if not self.validate_credentials():
                logger.warning(f"[{self.name}] Credentials not configured")
                return False

            # Default: try to make a simple request
            # Subclasses should override with specific health check endpoint
            return True

        except Exception as e:
            logger.error(f"[{self.name}] Health check failed: {e}")
            return False

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get client metrics.

        Returns:
            Dict with request count, error count, avg response time, etc.
        """
        avg_response_time = (
            self._total_response_time / self._request_count
            if self._request_count > 0
            else 0
        )

        return {
            "name": self.name,
            "base_url": self.base_url,
            "request_count": self._request_count,
            "error_count": self._error_count,
            "error_rate": (
                self._error_count / self._request_count
                if self._request_count > 0
                else 0
            ),
            "avg_response_time_ms": avg_response_time,
            "last_request_time": self._last_request_time,
        }

    def reset_metrics(self):
        """Reset all metrics to zero."""
        self._request_count = 0
        self._error_count = 0
        self._total_response_time = 0.0
        self._last_request_time = None

    def close(self):
        """Close the session and release resources."""
        self._session.close()
        logger.info(f"[{self.name}] Session closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
