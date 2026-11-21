# Authentication

`googlepy` supports three authentication modes. All of them resolve **scopes**
from configuration (see [Configuration](configuration.md)) and return standard
Google credential objects — the caller decides how to use them.

| Mode | Use when | Entry point |
|------|----------|-------------|
| **Service account** | Server-to-server, no user interaction | `service_account_credentials_from_env` / `build_service_account_credentials` |
| **OAuth 2.0** | Acting on behalf of an end user (consent) | `build_oauth_credentials` |
| **API key** | Public, read-only endpoints | `api_key_provider` |

## One generic entry point: `credentials_from_env`

If the mode itself is configuration-driven, use the single generic dispatcher
instead of a mode-specific builder. It takes an `AuthKind` (or its string value)
and sources every secret from the environment:

```python
from googlepy import credentials_from_env, AuthKind

sa_creds    = credentials_from_env(AuthKind.SERVICE_ACCOUNT, service="sheets")
user_creds  = credentials_from_env(AuthKind.OAUTH, service="calendar")
api_key     = credentials_from_env(AuthKind.API_KEY)          # returns the key str
same        = credentials_from_env("service_account", service="sheets")  # str kind
```

`AuthKind` is a `str`-backed `enum.Enum`, and the function is overloaded so a
type checker infers the exact return type per kind
(`service_account.Credentials`, user `Credentials`, or `str`). An unknown kind
raises `ValueError`. The per-mode helpers below remain available — for example
`service_account_credentials_from_env` is a thin wrapper over this dispatcher.

## Service account

Server-to-server auth using a downloaded JSON key.

### From `.env` (recommended)

Keep the key file out of code and point to it from the environment. Set the path
once in `.env`:

```dotenv
# .env
SERVICE_KEY_FILE=./service_key.json
```

Then load credentials with no file argument — the path is read from
`SERVICE_KEY_FILE` (or `GOOGLE_APPLICATION_CREDENTIALS`):

```python
from googlepy import service_account_credentials_from_env

creds = service_account_credentials_from_env(service="sheets")
```

`service_account_credentials_from_env` is a thin, intent-revealing wrapper over
`build_service_account_credentials` that takes no file/info arguments, so the
`.env`-driven source is unambiguous at the call site. It raises `ValueError` if
no key file is configured or the configured file does not exist.

### Explicit file or parsed JSON

```python
from googlepy import build_service_account_credentials

# From a key file (path resolved from SERVICE_KEY_FILE if omitted)
creds = build_service_account_credentials(
    key_file="service_key.json",
    service="sheets",            # resolves sheets-specific scopes
)

# Or directly from parsed JSON (e.g. loaded from a secret manager)
creds = build_service_account_credentials(key_info=key_dict, service="drive")
```

Obtain a key from the Google Cloud Console → *IAM & Admin* → *Service Accounts* →
*Keys* → *Add key* → *JSON*. Point `SERVICE_KEY_FILE` (or
`GOOGLE_APPLICATION_CREDENTIALS`) at the file, or pass `key_file`/`key_info`.
The file itself should never be committed — the repo's `.gitignore` already
excludes `service_key*.json`.

## OAuth 2.0 (user consent)

Runs the installed-app consent flow and caches the token for reuse. Expired
tokens with a refresh token are refreshed automatically.

```python
from googlepy import build_oauth_credentials

creds = build_oauth_credentials(
    client_secret_file="client_secret.json",  # or CLIENT_SECRET_FILE
    token_file="token.json",                   # cached here after first consent
    service="calendar",
)
```

Create an *OAuth client ID* (type *Desktop app*) in the Google Cloud Console and
download the client-secret JSON.

## API key

For endpoints that accept a key rather than a credential.

```python
from googlepy import api_key_provider

get_key = api_key_provider()   # reads GOOGLE_API_KEY if not passed
api_key = get_key()
```

## Lazy providers & cached clients

Each mode has a **provider** variant returning a zero-argument closure, so
credentials are built only on first use. `client_factory` wraps a provider and
caches the authorized `gspread` client.

```python
from googlepy import service_account_provider, client_factory

provider = service_account_provider(service="sheets")
get_client = client_factory(provider)   # lazily builds & caches the client

client = get_client()   # built here
client = get_client()   # reused
```

`client_factory` is generic over the client type. By default it authorizes a
`gspread` client, but pass `build=` to produce — and correctly type — any client:

```python
from googleapiclient.discovery import build as google_build

get_drive = client_factory(
    provider,
    build=lambda creds: google_build("drive", "v3", credentials=creds),
)
drive = get_drive()   # typed as the googleapiclient Resource
```

See the [Auth API reference](api/auth.md) for full signatures.
