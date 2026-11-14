"""Protocols and typing definitions for googlepy.

Defines structural subtyping protocols (PEP 544) to ensure decoupled,
stateless, and testable interfaces across credential providers and HTTP clients.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping, Protocol, Sequence, TypeVar, runtime_checkable
from google.auth.credentials import Credentials
import requests

T = TypeVar("T")
R = TypeVar("R")


@runtime_checkable
class CredentialsProvider(Protocol):
    """Protocol for a zero-argument callable that produces authorized Google Credentials."""

    def __call__(self) -> Credentials:
        """Yield valid, authorized Google Credentials on demand."""
        ...


@runtime_checkable
class HTTPClientProtocol(Protocol):
    """Protocol for an HTTP client capable of executing authorized requests."""

    def request(
        self,
        method: str,
        url: str,
        *,
        params: Mapping[str, Any] | None = None,
        json: Any = None,
        data: Any = None,
        headers: Mapping[str, str] | None = None,
        timeout: float = 30.0,
    ) -> requests.Response:
        """Execute an HTTP request and return the response."""
        ...


@runtime_checkable
class ServiceClientProtocol(Protocol):
    """Protocol for a Google service client offering REST verb helpers."""

    def get(self, endpoint: str, params: Mapping[str, Any] | None = None, **kwargs: Any) -> Any:
        ...

    def post(self, endpoint: str, json: Any = None, **kwargs: Any) -> Any:
        ...

    def put(self, endpoint: str, json: Any = None, **kwargs: Any) -> Any:
        ...

    def patch(self, endpoint: str, json: Any = None, **kwargs: Any) -> Any:
        ...

    def delete(self, endpoint: str, params: Mapping[str, Any] | None = None, **kwargs: Any) -> Any:
        ...
