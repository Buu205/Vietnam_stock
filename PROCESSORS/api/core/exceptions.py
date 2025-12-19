"""
API Exceptions
==============

Custom exceptions for API error handling.
"""


class APIError(Exception):
    """Base exception for all API errors."""

    def __init__(self, message: str, api_name: str = None, status_code: int = None):
        self.message = message
        self.api_name = api_name
        self.status_code = status_code
        super().__init__(self.message)

    def __str__(self):
        parts = [self.message]
        if self.api_name:
            parts.insert(0, f"[{self.api_name}]")
        if self.status_code:
            parts.append(f"(HTTP {self.status_code})")
        return " ".join(parts)


class APITimeoutError(APIError):
    """Raised when API request times out."""

    def __init__(self, api_name: str, timeout: float, endpoint: str = None):
        message = f"Request timed out after {timeout}s"
        if endpoint:
            message += f" for endpoint: {endpoint}"
        super().__init__(message, api_name)
        self.timeout = timeout
        self.endpoint = endpoint


class APIConnectionError(APIError):
    """Raised when unable to connect to API."""

    def __init__(self, api_name: str, url: str, original_error: Exception = None):
        message = f"Failed to connect to {url}"
        if original_error:
            message += f": {str(original_error)}"
        super().__init__(message, api_name)
        self.url = url
        self.original_error = original_error


class APIAuthenticationError(APIError):
    """Raised when API authentication fails."""

    def __init__(self, api_name: str, reason: str = None):
        message = "Authentication failed"
        if reason:
            message += f": {reason}"
        super().__init__(message, api_name, status_code=401)
        self.reason = reason


class APIRateLimitError(APIError):
    """Raised when API rate limit is exceeded."""

    def __init__(self, api_name: str, retry_after: int = None):
        message = "Rate limit exceeded"
        if retry_after:
            message += f", retry after {retry_after}s"
        super().__init__(message, api_name, status_code=429)
        self.retry_after = retry_after


class APIResponseError(APIError):
    """Raised when API returns an error response."""

    def __init__(self, api_name: str, status_code: int, response_body: str = None):
        message = f"API returned error"
        if response_body:
            message += f": {response_body[:200]}"
        super().__init__(message, api_name, status_code)
        self.response_body = response_body


class APIDataError(APIError):
    """Raised when API response data is invalid or unexpected."""

    def __init__(self, api_name: str, reason: str):
        message = f"Invalid data: {reason}"
        super().__init__(message, api_name)
        self.reason = reason


class APIConfigError(APIError):
    """Raised when API configuration is missing or invalid."""

    def __init__(self, api_name: str, config_key: str):
        message = f"Missing or invalid configuration: {config_key}"
        super().__init__(message, api_name)
        self.config_key = config_key
