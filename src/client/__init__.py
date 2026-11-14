"""Compatibility module: forwards to googlepy.client."""

from googlepy.client import (
    GoogleAPIError,
    GoogleClientType,
    GoogleServiceClient,
    get_calendar_client,
    get_client,
    get_client_service_file,
    get_client_with_api_key,
    get_docs_client,
    get_drive_client,
    get_gmail_client,
    get_service_client,
    get_sheets_client,
)

__all__ = [
    "GoogleClientType",
    "GoogleAPIError",
    "GoogleServiceClient",
    "get_service_client",
    "get_sheets_client",
    "get_drive_client",
    "get_docs_client",
    "get_gmail_client",
    "get_calendar_client",
    "get_client",
    "get_client_service_file",
    "get_client_with_api_key",
]
