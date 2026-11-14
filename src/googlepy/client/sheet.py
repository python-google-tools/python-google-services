from __future__ import annotations

import os
from typing import Any
import gspread
from google.auth.credentials import Credentials

from googlepy.auth.models import ApiKeyAuth
from googlepy.auth.provider import build_oauth_credentials, build_service_account_credentials
from googlepy.client.base import GoogleClientType
from googlepy.config.env import GOOGLE_API_KEY, GOOGLE_SERVICE_KEY_FILE


def get_client_service_file(service_key_file: str | None = None) -> gspread.Client:
    """Create a gspread client using the provided service key file or env var."""
    key_file = service_key_file or GOOGLE_SERVICE_KEY_FILE
    if not key_file or not os.path.isfile(key_file):
        raise ValueError(
            f"Service key file not found: '{key_file}'. "
            "Pass service_key_file or set GOOGLE_SERVICE_KEY_FILE / SERVICE_KEY_FILE environment variable."
        )
    return gspread.service_account(filename=key_file)


def get_client_with_api_key(api_key: str | None = None) -> gspread.Client:
    """Create a gspread client using an API key."""
    key = api_key or GOOGLE_API_KEY or ""
    validated = ApiKeyAuth(api_key=key)
    return gspread.api_key(validated.api_key)


def get_sheets_client(
    credentials: Credentials | None = None,
    client_type: GoogleClientType = GoogleClientType.SERVICE_ACCOUNT,
    service_key_file: str | None = None,
    client_secret_file: str | None = None,
    token_file: str | None = None,
    api_key: str | None = None,
) -> gspread.Client:
    """Get an authenticated gspread Client instance."""
    if credentials is not None:
        return gspread.authorize(credentials)

    if client_type == GoogleClientType.SERVICE_ACCOUNT:
        creds = build_service_account_credentials(key_file=service_key_file, service="sheets")
        return gspread.authorize(creds)
    elif client_type == GoogleClientType.OAUTH2:
        creds = build_oauth_credentials(
            client_secret_file=client_secret_file, token_file=token_file, service="sheets"
        )
        return gspread.authorize(creds)
    elif client_type == GoogleClientType.API_KEY:
        return get_client_with_api_key(api_key)
    else:
        raise ValueError(f"Unsupported client type: {client_type}")


def get_client(TYPE: GoogleClientType = GoogleClientType.SERVICE_ACCOUNT) -> gspread.Client:
    """Create a gspread client using default credentials. Backward-compatible helper."""
    if TYPE == GoogleClientType.SERVICE_ACCOUNT:
        return get_client_service_file()
    elif TYPE == GoogleClientType.API_KEY:
        return get_client_with_api_key()
    elif TYPE == GoogleClientType.OAUTH2:
        return get_sheets_client(client_type=GoogleClientType.OAUTH2)
    else:
        raise ValueError(f"Unsupported client type: {TYPE}")
