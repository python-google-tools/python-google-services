"""Higher-order decorators for resilient Google API client operations.

Implements exponential backoff with jitter for transient HTTP errors
and lightweight TTL memoization closures.
"""

from __future__ import annotations

import functools
import random
import time
from typing import Any, Callable, Sequence, TypeVar

from googlepy.exceptions import GoogleAPIError

F = TypeVar("F", bound=Callable[..., Any])


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 30.0,
    retry_statuses: Sequence[int] = (429, 500, 502, 503, 504),
    sleep_func: Callable[[float], None] = time.sleep,
) -> Callable[[F], F]:
    """Decorator to retry a function on transient Google API errors with exponential backoff and jitter.

    Args:
        max_retries: Maximum number of retry attempts before giving up.
        base_delay: Initial delay in seconds.
        max_delay: Maximum delay cap in seconds.
        retry_statuses: HTTP status codes considered transient.
        sleep_func: Callable used for pausing execution (injectable for testing).

    Returns:
        Decorated function with automatic retry behavior.

    Raises:
        GoogleAPIError: If non-transient status or max retries exhausted.
        Exception: Any other unexpected exception raised by the target function.
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempts = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except GoogleAPIError as err:
                    attempts += 1
                    if attempts > max_retries or err.status_code not in retry_statuses:
                        raise err

                    # Exponential backoff with full jitter: Uniform(0.1, min(max_delay, base_delay * 2^attempts))
                    calculated_delay = min(max_delay, base_delay * (2 ** (attempts - 1)))
                    jittered_delay = random.uniform(0.1, max(0.1, calculated_delay))
                    sleep_func(jittered_delay)

        return wrapper  # type: ignore

    return decorator


def memoize_with_ttl(ttl_seconds: float = 300.0) -> Callable[[F], F]:
    """Closure-based memoization decorator with time-to-live expiration.

    Args:
        ttl_seconds: Cache lifespan in seconds.

    Returns:
        Decorated callable that caches results for the duration of ttl_seconds.
    """
    def decorator(func: F) -> F:
        cache: dict[tuple[Any, ...], tuple[float, Any]] = {}

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = (args, tuple(sorted(kwargs.items())))
            now = time.monotonic()
            if key in cache:
                timestamp, cached_result = cache[key]
                if now - timestamp < ttl_seconds:
                    return cached_result

            result = func(*args, **kwargs)
            cache[key] = (now, result)
            return result

        def cache_clear() -> None:
            cache.clear()

        wrapper.cache_clear = cache_clear  # type: ignore
        return wrapper  # type: ignore

    return decorator
