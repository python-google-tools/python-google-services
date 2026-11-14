from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

from googlepy.config.default import get_default_config

load_dotenv()


def _get_default_scopes() -> list[str]:
    try:
        scopes = get_default_config(["google", "scopes"])
        if isinstance(scopes, list):
            return scopes
    except Exception:
        pass
    try:
        scopes = get_default_config(["oauth", "scopes"])
        if isinstance(scopes, list):
            return scopes
    except Exception:
        pass
    return [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]


# Google API scopes for accessing Google services
_env_scopes = os.getenv("GOOGLE_SCOPES")
if _env_scopes:
    GOOGLE_SCOPES = [s.strip() for s in _env_scopes.split(",") if s.strip()]
else:
    GOOGLE_SCOPES = _get_default_scopes()

# Service account credentials file
GOOGLE_SERVICE_KEY_FILE = os.getenv("SERVICE_KEY_FILE") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# OAuth 2.0 configuration files
CLIENT_SECRET_FILE = os.getenv("CLIENT_SECRET_FILE") or os.getenv("GOOGLE_CLIENT_SECRET_FILE") or "client_secret.json"
TOKEN_FILE = os.getenv("TOKEN_FILE") or "token.json"

# API keys and OAuth secrets
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# Google Sheets specific identifiers
GOOGLE_URL = os.getenv("GOOGLE_URL")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")
