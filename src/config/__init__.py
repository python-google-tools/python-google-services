"""Compatibility module: forwards to googlepy.config."""

from googlepy.config import (
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
    find_default_config_path,
    get_default_config,
)

__all__ = [
    "find_default_config_path",
    "get_default_config",
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
