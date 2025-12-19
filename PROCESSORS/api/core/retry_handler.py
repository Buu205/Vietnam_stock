"""
Retry Handler
=============

Retry logic with exponential backoff for API requests.
"""

import time
import random
import logging
from dataclasses import dataclass, field
from typing import Callable, TypeVar, List, Type
from functools import wraps

from PROCESSORS.api.core.exceptions import (
    APIError,
    APITimeoutError,
    APIConnectionError,
    APIRateLimitError,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    max_retries: int = 3
    base_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    exponential_base: float = 2.0
    jitter: bool = True  # Add randomness to delay
    retryable_exceptions: List[Type[Exception]] = field(
        default_factory=lambda: [
            APITimeoutError,
            APIConnectionError,
            APIRateLimitError,
            ConnectionError,
            TimeoutError,
        ]
    )
    retryable_status_codes: List[int] = field(
        default_factory=lambda: [408, 429, 500, 502, 503, 504]
    )


class RetryHandler:
    """
    Handles retry logic with exponential backoff.

    Features:
    - Exponential backoff with optional jitter
    - Configurable retry attempts and delays
    - Respects rate limit headers (Retry-After)
    - Detailed logging of retry attempts
    """

    def __init__(self, config: RetryConfig = None):
        self.config = config or RetryConfig()

    def calculate_delay(self, attempt: int, retry_after: int = None) -> float:
        """
        Calculate delay before next retry.

        Args:
            attempt: Current attempt number (0-indexed)
            retry_after: Optional server-specified retry delay

        Returns:
            Delay in seconds
        """
        if retry_after:
            return min(retry_after, self.config.max_delay)

        delay = self.config.base_delay * (self.config.exponential_base**attempt)

        if self.config.jitter:
            # Add 0-50% jitter
            delay = delay * (1 + random.random() * 0.5)

        return min(delay, self.config.max_delay)

    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """
        Determine if request should be retried.

        Args:
            exception: The exception that occurred
            attempt: Current attempt number

        Returns:
            True if should retry, False otherwise
        """
        if attempt >= self.config.max_retries:
            return False

        # Check if exception type is retryable
        for exc_type in self.config.retryable_exceptions:
            if isinstance(exception, exc_type):
                return True

        # Check if API error with retryable status code
        if isinstance(exception, APIError) and exception.status_code:
            if exception.status_code in self.config.retryable_status_codes:
                return True

        return False

    def execute_with_retry(
        self,
        func: Callable[[], T],
        api_name: str = "unknown",
        endpoint: str = None,
    ) -> T:
        """
        Execute function with retry logic.

        Args:
            func: Function to execute
            api_name: Name of API for logging
            endpoint: Endpoint being called for logging

        Returns:
            Result of function execution

        Raises:
            Exception: The last exception if all retries fail
        """
        last_exception = None
        endpoint_str = endpoint or "unknown"

        for attempt in range(self.config.max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(
                        f"[{api_name}] Retry attempt {attempt}/{self.config.max_retries} "
                        f"for {endpoint_str}"
                    )
                return func()

            except Exception as e:
                last_exception = e
                retry_after = getattr(e, "retry_after", None)

                if not self.should_retry(e, attempt):
                    logger.error(
                        f"[{api_name}] Non-retryable error for {endpoint_str}: {e}"
                    )
                    raise

                delay = self.calculate_delay(attempt, retry_after)
                logger.warning(
                    f"[{api_name}] Request failed for {endpoint_str}: {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                time.sleep(delay)

        # All retries exhausted
        logger.error(
            f"[{api_name}] All {self.config.max_retries} retries exhausted "
            f"for {endpoint_str}"
        )
        raise last_exception


def with_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    retryable_exceptions: List[Type[Exception]] = None,
):
    """
    Decorator for adding retry logic to functions.

    Usage:
        @with_retry(max_retries=3, base_delay=1.0)
        def fetch_data():
            ...
    """
    if retryable_exceptions is None:
        retryable_exceptions = [
            APITimeoutError,
            APIConnectionError,
            ConnectionError,
            TimeoutError,
        ]

    config = RetryConfig(
        max_retries=max_retries,
        base_delay=base_delay,
        retryable_exceptions=retryable_exceptions,
    )
    handler = RetryHandler(config)

    def decorator(func: Callable[[], T]) -> Callable[[], T]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return handler.execute_with_retry(
                lambda: func(*args, **kwargs),
                api_name=getattr(func, "__name__", "unknown"),
            )

        return wrapper

    return decorator
