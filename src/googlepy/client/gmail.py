from __future__ import annotations

from typing import Any
from google.auth.credentials import Credentials

from googlepy.auth.provider import build_oauth_credentials, build_service_account_credentials
from googlepy.client.base import GoogleClientType, GoogleServiceClient

GMAIL_V1_BASE_URL = "https://gmail.googleapis.com/gmail/v1"


def get_gmail_client(
    credentials: Credentials | None = None,
    client_type: GoogleClientType = GoogleClientType.SERVICE_ACCOUNT,
    service_key_file: str | None = None,
    client_secret_file: str | None = None,
    token_file: str | None = None,
    api_key: str | None = None,
    base_url: str = GMAIL_V1_BASE_URL,
    session: Any = None,
) -> GoogleServiceClient:
    """Create an authenticated Gmail API v1 client."""
    if session is not None or credentials is not None:
        return GoogleServiceClient(credentials=credentials, base_url=base_url, session=session, api_key=api_key)

    if client_type == GoogleClientType.SERVICE_ACCOUNT:
        creds = build_service_account_credentials(key_file=service_key_file, service="gmail")
        return GoogleServiceClient(credentials=creds, base_url=base_url)
    elif client_type == GoogleClientType.OAUTH2:
        creds = build_oauth_credentials(
            client_secret_file=client_secret_file, token_file=token_file, service="gmail"
        )
        return GoogleServiceClient(credentials=creds, base_url=base_url)
    elif client_type == GoogleClientType.API_KEY:
        return GoogleServiceClient(base_url=base_url, api_key=api_key)
    else:
        raise ValueError(f"Unsupported client type for Gmail: {client_type}")
