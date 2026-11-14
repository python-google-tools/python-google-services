"""Standard exception hierarchy for googlepy."""

from __future__ import annotations

from typing import Any


class GooglePyError(Exception):
    """Base exception for all googlepy errors."""


class GoogleAPIError(GooglePyError):
    """Raised when a Google REST API responds with an error status code.

    Attributes:
        status_code: The HTTP status code (e.g. 400, 401, 403, 404, 429, 500).
        message: Human-readable error message.
        details: Parsed JSON error details from the Google API error response, if any.
    """

    def __init__(self, status_code: int, message: str, details: Any = None):
        super().__init__(f"Google API Error [{status_code}]: {message}")
        self.status_code = status_code
        self.message = message
        self.details = details


class ConfigurationError(GooglePyError):
    """Raised when configuration or asset paths cannot be resolved."""


class AuthenticationError(GooglePyError):
    """Raised when authentication credentials cannot be constructed or refreshed."""
