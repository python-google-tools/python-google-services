from __future__ import annotations

from typing import Any
from google.auth.credentials import Credentials

from googlepy.client.base import GoogleClientType, GoogleServiceClient
from googlepy.client.calendar import get_calendar_client
from googlepy.client.docs import get_docs_client
from googlepy.client.drive import get_drive_client
from googlepy.client.gmail import get_gmail_client
from googlepy.client.sheet import get_sheets_client

SERVICE_FACTORIES = {
    "sheets": get_sheets_client,
    "drive": get_drive_client,
    "docs": get_docs_client,
    "gmail": get_gmail_client,
    "calendar": get_calendar_client,
}


def get_service_client(
    service_name: str,
    credentials: Credentials | None = None,
    client_type: GoogleClientType = GoogleClientType.SERVICE_ACCOUNT,
    **kwargs: Any,
) -> Any:
    """Dynamic factory to create an authenticated client for any supported Google service.

    :param service_name: 'sheets', 'drive', 'docs', 'gmail', or 'calendar'.
    :param credentials: Optional pre-built credentials.
    :param client_type: Type of authentication to use.
    :param kwargs: Service-specific overrides (key_file, token_file, base_url, etc.).
    """
    key = service_name.lower().strip()
    if key in SERVICE_FACTORIES:
        factory = SERVICE_FACTORIES[key]
        return factory(credentials=credentials, client_type=client_type, **kwargs)

    # Generic Google REST API fallback
    base_url = kwargs.get("base_url", f"https://{key}.googleapis.com/v1")
    return GoogleServiceClient(credentials=credentials, base_url=base_url, **kwargs)
