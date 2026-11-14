"""Compatibility module: forwards to googlepy.client.sheet."""

from googlepy.client.base import GoogleClientType
from googlepy.client.sheet import (
    get_client,
    get_client_service_file,
    get_client_with_api_key,
    get_sheets_client,
)

__all__ = [
    "GoogleClientType",
    "get_client_service_file",
    "get_client_with_api_key",
    "get_sheets_client",
    "get_client",
]
