from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, Sequence

from googlepy.config.default import get_default_config

DEFAULT_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar",
]

SHEETS_SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

DRIVE_SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
]

DOCS_SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]

GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
]

CALENDAR_SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
]

SERVICE_SCOPES: dict[str, list[str]] = {
    "sheets": SHEETS_SCOPES,
    "drive": DRIVE_SCOPES,
    "docs": DOCS_SCOPES,
    "gmail": GMAIL_SCOPES,
    "calendar": CALENDAR_SCOPES,
}


def resolve_scopes(
    service: str | None = None,
    scopes: Iterable[str] | None = None,
    config_path: str | Path | None = None,
) -> list[str]:
    """Resolve Google API scopes in strict priority order:

    1. Explicit ``scopes`` argument (if provided and non-empty).
    2. ``GOOGLE_SCOPES`` environment variable (comma-separated list).
    3. TOML configuration file (service-specific or global).
    4. Built-in service scopes or global defaults.

    :param service: Optional service name ('sheets', 'drive', 'docs', 'gmail', 'calendar').
    :param scopes: Optional explicit list of scopes.
    :param config_path: Optional path to config TOML file.
    :return: List of resolved scope URLs.
    """
    if scopes:
        resolved = [s.strip() for s in scopes if s and s.strip()]
        if resolved:
            return resolved

    env = os.getenv("GOOGLE_SCOPES", "").strip()
    if env:
        parsed = [s.strip() for s in env.split(",") if s.strip()]
        if parsed:
            return parsed

    # Check TOML configuration
    try:
        if service:
            svc_scopes = get_default_config(
                ["google", "scopes_by_service", service.lower()],
                config_path=config_path,
            )
            if isinstance(svc_scopes, list) and svc_scopes:
                return [s.strip() for s in svc_scopes if s.strip()]
    except Exception:
        pass

    try:
        global_scopes = get_default_config(["google", "scopes"], config_path=config_path)
        if isinstance(global_scopes, list) and global_scopes:
            return [s.strip() for s in global_scopes if s.strip()]
    except Exception:
        pass

    try:
        oauth_scopes = get_default_config(["oauth", "scopes"], config_path=config_path)
        if isinstance(oauth_scopes, list) and oauth_scopes:
            return [s.strip() for s in oauth_scopes if s.strip()]
    except Exception:
        pass

    # Built-in fallback
    if service and service.lower() in SERVICE_SCOPES:
        return list(SERVICE_SCOPES[service.lower()])

    return list(DEFAULT_SCOPES)
