"""Compatibility module: forwards to googlepy.config.env."""

from googlepy.config.env import (
    CLIENT_SECRET_FILE,
    GOOGLE_API_KEY,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_SCOPES,
    GOOGLE_SERVICE_KEY_FILE,
    GOOGLE_SHEET_ID,
    GOOGLE_SHEET_NAME,
    GOOGLE_URL,
    TOKEN_FILE,
)

__all__ = [
    "GOOGLE_SCOPES",
    "GOOGLE_SERVICE_KEY_FILE",
    "CLIENT_SECRET_FILE",
    "TOKEN_FILE",
    "GOOGLE_API_KEY",
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "GOOGLE_URL",
    "GOOGLE_SHEET_ID",
    "GOOGLE_SHEET_NAME",
]
