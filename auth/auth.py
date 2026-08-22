"""Reusable, closure-based Google authentication for gspread.

The design is provider closures: you configure a credential source once
(service account or OAuth) and receive a **zero-argument closure** that yields
authorized credentials on demand. Building a provider is cheap and side-effect
free — all validation, file, and network I/O is deferred until the closure is
actually called. Wrap a provider with :func:`client_factory` to get a lazily
built, cached ``gspread`` client.

    from auth.auth import service_account_provider, client_factory

    get_client = client_factory(service_account_provider("key.json"))
    client = get_client()        # built here, reused on later calls
"""

import os

from dotenv import load_dotenv

load_dotenv()

DEFAULT_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_scopes(scopes=None):
    """Resolve scopes: explicit ``scopes`` > ``GOOGLE_SCOPES`` env > defaults."""
    if scopes:
        return list(scopes)
    env = os.getenv("GOOGLE_SCOPES", "")
    parsed = [s.strip() for s in env.split(",") if s.strip()]
    return parsed or list(DEFAULT_SCOPES)


def service_account_provider(key_file=None, scopes=None):
    """Return a closure ``() -> Credentials`` for a service account.

    Nothing is read or validated until the returned closure is invoked.

    :param key_file: path to the service-account JSON key. Falls back to the
        ``SERVICE_KEY_FILE`` environment variable.
    :param scopes: iterable of scopes; resolved via :func:`get_scopes`.
    """
    key_file = key_file or os.getenv("SERVICE_KEY_FILE", "")
    resolved_scopes = get_scopes(scopes)

    def provider():
        from google.oauth2 import service_account

        if not resolved_scopes:
            raise ValueError(
                "At least one scope is required (set GOOGLE_SCOPES or pass scopes)."
            )
        if not key_file or not os.path.isfile(key_file):
            raise ValueError(
                "Service account key file not found; "
                "set SERVICE_KEY_FILE or pass key_file."
            )
        return service_account.Credentials.from_service_account_file(
            key_file, scopes=resolved_scopes
        )

    return provider


def oauth_provider(client_secret_file=None, scopes=None, token_file="token.json"):
    """Return a closure ``() -> Credentials`` for the OAuth user-consent flow.

    On invocation the closure loads a cached token if valid, refreshes it if
    expired, or runs the installed-app consent flow, persisting the result to
    ``token_file``. All deferred until the closure is called.

    :param client_secret_file: OAuth client secret JSON. Falls back to the
        ``CLIENT_SECRET_FILE`` environment variable.
    :param scopes: iterable of scopes; resolved via :func:`get_scopes`.
    :param token_file: where the refreshed user token is cached.
    """
    client_secret_file = client_secret_file or os.getenv(
        "CLIENT_SECRET_FILE", "client_secret.json"
    )
    resolved_scopes = get_scopes(scopes)

    def provider():
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow

        if not resolved_scopes:
            raise ValueError(
                "At least one scope is required (set GOOGLE_SCOPES or pass scopes)."
            )

        creds = None
        if os.path.isfile(token_file):
            creds = Credentials.from_authorized_user_file(token_file, resolved_scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.isfile(client_secret_file):
                    raise ValueError(
                        "OAuth client secret file not found; "
                        "set CLIENT_SECRET_FILE or pass client_secret_file."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secret_file, resolved_scopes
                )
                creds = flow.run_local_server(port=0)
            with open(token_file, "w", encoding="utf-8") as fh:
                fh.write(creds.to_json())

        return creds

    return provider


def client_factory(credentials_provider, *, verify=False):
    """Wrap a credentials provider in a closure that returns a cached client.

    The ``gspread`` client is built on first call and reused thereafter, so the
    credentials provider runs at most once.

    :param credentials_provider: a zero-arg closure returning credentials, e.g.
        the result of :func:`service_account_provider` or :func:`oauth_provider`.
    :param verify: when True, make a single connectivity call the first time the
        client is built (raises if auth/network fails).
    """
    cache = {}

    def get_client():
        if "client" not in cache:
            import gspread

            client = gspread.authorize(credentials_provider())
            if verify:
                client.list_spreadsheet_files()
            cache["client"] = client
        return cache["client"]

    return get_client


def get_client():
    """Legacy helper: verified, service-account ``gspread`` client from env."""
    return client_factory(service_account_provider(), verify=True)()
