from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable, Iterable

from google.oauth2 import service_account
from google.oauth2.credentials import Credentials

from googlepy.auth.models import ApiKeyAuth, OAuthAuth, ServiceAccountAuth
from googlepy.auth.scopes import DEFAULT_SCOPES, resolve_scopes
from googlepy.config.env import CLIENT_SECRET_FILE, GOOGLE_API_KEY, GOOGLE_SERVICE_KEY_FILE, TOKEN_FILE


def get_scopes(
    scopes: Iterable[str] | None = None,
    service: str | None = None,
    config_path: str | Path | None = None,
) -> list[str]:
    """Backward-compatible helper to resolve scopes."""
    return resolve_scopes(service=service, scopes=scopes, config_path=config_path)


def build_service_account_credentials(
    key_file: str | Path | None = None,
    key_info: dict[str, Any] | None = None,
    scopes: Iterable[str] | None = None,
    service: str | None = None,
) -> service_account.Credentials:
    """Instantly build authorized credentials from a service-account JSON key.

    :param key_file: Path to service-account JSON key.
    :param key_info: Dict containing service account JSON data.
    :param scopes: Explicit scopes list.
    :param service: Service name to resolve default scopes for.
    """
    resolved_scopes = resolve_scopes(service=service, scopes=scopes)
    if not resolved_scopes:
        raise ValueError("At least one scope is required to authenticate.")

    if key_info:
        auth_model = ServiceAccountAuth(key_info=key_info)
        return service_account.Credentials.from_service_account_info(
            auth_model.key_info, scopes=resolved_scopes
        )

    file_path = str(key_file or GOOGLE_SERVICE_KEY_FILE or "").strip()
    if not file_path or not os.path.isfile(file_path):
        raise ValueError(
            f"Service account key file not found: '{file_path}'. "
            "Set SERVICE_KEY_FILE or GOOGLE_APPLICATION_CREDENTIALS, or pass key_file."
        )

    auth_model = ServiceAccountAuth(key_file=file_path)
    return service_account.Credentials.from_service_account_file(
        auth_model.key_file, scopes=resolved_scopes
    )


def service_account_credentials_from_env(
    scopes: Iterable[str] | None = None,
    service: str | None = None,
) -> service_account.Credentials:
    """Build service-account credentials from the ``.env``-configured key file.

    Convenience entry point for the common case where the service-account JSON
    key path lives in the environment. The path is read from ``SERVICE_KEY_FILE``
    (or ``GOOGLE_APPLICATION_CREDENTIALS``) via :data:`GOOGLE_SERVICE_KEY_FILE`;
    scopes are resolved explicit > per-service default > global default.

    This is a thin, intent-revealing wrapper over
    :func:`build_service_account_credentials` that takes no file/info arguments,
    so the ``.env``-driven source is unambiguous at the call site.

    Args:
        scopes: Explicit scopes; overrides any service/global defaults.
        service: Service name (e.g. ``"sheets"``) whose default scopes to use
            when ``scopes`` is not given.

    Returns:
        Authorized ``service_account.Credentials``.

    Raises:
        ValueError: If no key file is configured in the environment or the
            configured file does not exist, or if no scopes resolve.
    """
    return build_service_account_credentials(scopes=scopes, service=service)


def build_oauth_credentials(
    client_secret_file: str | Path | None = None,
    scopes: Iterable[str] | None = None,
    token_file: str | Path | None = None,
    service: str | None = None,
    port: int = 0,
) -> Credentials:
    """Build authorized user credentials via OAuth 2.0 flow.

    Refreshes expired credentials if refresh_token is present; otherwise triggers
    local server consent flow and saves token to token_file.
    """
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow

    resolved_scopes = resolve_scopes(service=service, scopes=scopes)
    if not resolved_scopes:
        raise ValueError("At least one scope is required for OAuth.")

    secret = str(client_secret_file or CLIENT_SECRET_FILE or "client_secret.json").strip()
    token = str(token_file or TOKEN_FILE or "token.json").strip()

    OAuthAuth(client_secret_file=secret, token_file=token)

    creds: Credentials | None = None
    if os.path.isfile(token):
        try:
            creds = Credentials.from_authorized_user_file(token, resolved_scopes)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.isfile(secret):
                raise ValueError(
                    f"OAuth client secret file not found: '{secret}'. "
                    "Set CLIENT_SECRET_FILE or pass client_secret_file."
                )
            flow = InstalledAppFlow.from_client_secrets_file(secret, resolved_scopes)
            creds = flow.run_local_server(port=port)

        # Cache refreshed or newly obtained token
        token_path = Path(token)
        token_path.parent.mkdir(parents=True, exist_ok=True)
        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

    return creds


def service_account_provider(
    key_file: str | Path | None = None,
    key_info: dict[str, Any] | None = None,
    scopes: Iterable[str] | None = None,
    service: str | None = None,
) -> Callable[[], service_account.Credentials]:
    """Return a zero-argument closure that provides service account credentials on demand."""
    def provider() -> service_account.Credentials:
        return build_service_account_credentials(
            key_file=key_file, key_info=key_info, scopes=scopes, service=service
        )

    return provider


def oauth_provider(
    client_secret_file: str | Path | None = None,
    scopes: Iterable[str] | None = None,
    token_file: str | Path | None = None,
    service: str | None = None,
    port: int = 0,
) -> Callable[[], Credentials]:
    """Return a zero-argument closure that provides OAuth user credentials on demand."""
    def provider() -> Credentials:
        return build_oauth_credentials(
            client_secret_file=client_secret_file,
            scopes=scopes,
            token_file=token_file,
            service=service,
            port=port,
        )

    return provider


def api_key_provider(api_key: str | None = None) -> Callable[[], str]:
    """Return a zero-argument closure that returns a validated API key."""
    key = api_key or GOOGLE_API_KEY or ""
    validated = ApiKeyAuth(api_key=key)

    def provider() -> str:
        return validated.api_key

    return provider


def client_factory(
    credentials_provider: Callable[[], Any],
    *,
    verify: bool = False,
) -> Callable[[], Any]:
    """Wrap a credentials provider in a closure that returns a cached gspread client.

    The client is lazily built on the first call and reused thereafter.

    Args:
        credentials_provider: A zero-argument callable returning credentials.
        verify: When True, performs a verification call on the first build.

    Returns:
        Zero-argument closure returning the cached authorized client.
    """
    cache: dict[str, Any] = {}

    def get_client() -> Any:
        if "client" not in cache:
            import gspread

            creds = credentials_provider()
            client = gspread.authorize(creds)
            if verify:
                client.list_spreadsheet_files()
            cache["client"] = client
        return cache["client"]

    return get_client
