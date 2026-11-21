from __future__ import annotations

import enum
import os
from pathlib import Path
from typing import Any, Callable, Iterable, Literal, TypeVar, Union, overload

from google.oauth2 import service_account
from google.oauth2.credentials import Credentials

from googlepy.auth.models import ApiKeyAuth, OAuthAuth, ServiceAccountAuth
from googlepy.auth.scopes import DEFAULT_SCOPES, resolve_scopes
from googlepy.config.env import CLIENT_SECRET_FILE, GOOGLE_API_KEY, GOOGLE_SERVICE_KEY_FILE, TOKEN_FILE

# Credentials returned by the env-driven dispatcher: OAuth/service-account
# credential objects, or a bare API-key string.
AnyCredentials = Union[service_account.Credentials, Credentials, str]

#: Type variable for the client object produced by :func:`client_factory`.
T = TypeVar("T")


class AuthKind(str, enum.Enum):
    """Supported credential sources for :func:`credentials_from_env`.

    Subclasses ``str`` so members compare equal to their string values and can
    be passed either as ``AuthKind.SERVICE_ACCOUNT`` or ``"service_account"``.
    """

    SERVICE_ACCOUNT = "service_account"
    OAUTH = "oauth"
    API_KEY = "api_key"


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
    return credentials_from_env(AuthKind.SERVICE_ACCOUNT, scopes=scopes, service=service)


@overload
def credentials_from_env(
    kind: Literal[AuthKind.SERVICE_ACCOUNT],
    *,
    scopes: Iterable[str] | None = ...,
    service: str | None = ...,
) -> service_account.Credentials: ...


@overload
def credentials_from_env(
    kind: Literal[AuthKind.OAUTH],
    *,
    scopes: Iterable[str] | None = ...,
    service: str | None = ...,
) -> Credentials: ...


@overload
def credentials_from_env(
    kind: Literal[AuthKind.API_KEY],
    *,
    scopes: Iterable[str] | None = ...,
    service: str | None = ...,
) -> str: ...


def credentials_from_env(
    kind: AuthKind | str,
    *,
    scopes: Iterable[str] | None = None,
    service: str | None = None,
) -> AnyCredentials:
    """Build credentials of any supported kind from ``.env`` configuration.

    A single generic entry point that dispatches on ``kind`` to the matching
    builder, each sourcing its secrets from the environment (see
    :mod:`googlepy.config.env`):

    - ``SERVICE_ACCOUNT`` → key file at ``SERVICE_KEY_FILE`` /
      ``GOOGLE_APPLICATION_CREDENTIALS``.
    - ``OAUTH`` → client secret / token at ``CLIENT_SECRET_FILE`` /
      ``TOKEN_FILE`` (runs the consent flow on first use).
    - ``API_KEY`` → ``GOOGLE_API_KEY`` (returns the validated key string).

    Args:
        kind: Which credential source to use. Accepts an :class:`AuthKind`
            member or its string value (e.g. ``"service_account"``).
        scopes: Explicit scopes; overrides service/global defaults. Ignored for
            ``API_KEY``.
        service: Service name (e.g. ``"sheets"``) whose default scopes to use
            when ``scopes`` is not given. Ignored for ``API_KEY``.

    Returns:
        ``service_account.Credentials`` for ``SERVICE_ACCOUNT``, user
        ``Credentials`` for ``OAUTH``, or the API-key ``str`` for ``API_KEY``.

    Raises:
        ValueError: If ``kind`` is not a valid :class:`AuthKind`, or the
            selected source is not configured in the environment.
    """
    resolved = AuthKind(kind)
    builders: dict[AuthKind, Callable[[], AnyCredentials]] = {
        AuthKind.SERVICE_ACCOUNT: lambda: build_service_account_credentials(
            scopes=scopes, service=service
        ),
        AuthKind.OAUTH: lambda: build_oauth_credentials(scopes=scopes, service=service),
        AuthKind.API_KEY: lambda: api_key_provider()(),
    }
    return builders[resolved]()


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
    build: Callable[[Any], T] | None = None,
) -> Callable[[], T]:
    """Wrap a credentials provider in a closure that returns a cached client.

    The client is lazily built on the first call and reused thereafter. Generic
    over the client type: by default it authorizes a ``gspread`` client, but any
    ``build`` callable mapping credentials to a client may be supplied, and the
    returned closure is typed to that client's type.

    Args:
        credentials_provider: A zero-argument callable returning credentials.
        verify: When True, performs a ``gspread`` verification call on the first
            build. Only applies to the default ``gspread`` client.
        build: Optional callable that turns credentials into a client. Defaults
            to ``gspread.authorize``.

    Returns:
        Zero-argument closure returning the cached authorized client.
    """
    cache: dict[str, T] = {}

    def get_client() -> T:
        if "client" not in cache:
            creds = credentials_provider()
            if build is None:
                import gspread

                client = gspread.authorize(creds)
                if verify:
                    client.list_spreadsheet_files()
            else:
                client = build(creds)
            cache["client"] = client
        return cache["client"]

    return get_client
