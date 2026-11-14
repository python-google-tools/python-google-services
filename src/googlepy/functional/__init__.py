"""Functional programming primitives and higher-order helpers for googlepy."""

from googlepy.functional.combinators import compose, curry, pipe
from googlepy.functional.decorators import memoize_with_ttl, retry_with_backoff
from googlepy.functional.pagination import paginate
from googlepy.functional.protocols import (
    CredentialsProvider,
    HTTPClientProtocol,
    ServiceClientProtocol,
)

__all__ = [
    "CredentialsProvider",
    "HTTPClientProtocol",
    "ServiceClientProtocol",
    "retry_with_backoff",
    "memoize_with_ttl",
    "pipe",
    "compose",
    "curry",
    "paginate",
]
