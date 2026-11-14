# Configuration

All runtime configuration is **dynamic** — nothing assumes a fixed install
location. Paths resolve relative to the package, so the library works at any
path inside any host project.

## Scope resolution

`resolve_scopes()` resolves the Google API scopes in strict priority order — the
first non-empty source wins:

1. **Explicit** `scopes=[...]` argument
2. **`GOOGLE_SCOPES`** environment variable (comma-separated)
3. **TOML config** — service-specific (`[google.scopes_by_service]`), then
   global (`[google] scopes`), then `[oauth] scopes`
4. **Built-in defaults** — per-service (`SERVICE_SCOPES`) or `DEFAULT_SCOPES`

```python
from googlepy import resolve_scopes

resolve_scopes(service="sheets")                 # sheets defaults
resolve_scopes(scopes=["https://.../drive"])     # explicit wins over everything
```

## Environment variables

Set these in the environment or a `.env` file (loaded automatically via
`python-dotenv`).

| Variable | Purpose |
|----------|---------|
| `GOOGLE_SCOPES` | Comma-separated scope override |
| `SERVICE_KEY_FILE` / `GOOGLE_APPLICATION_CREDENTIALS` | Service-account JSON key path |
| `CLIENT_SECRET_FILE` / `GOOGLE_CLIENT_SECRET_FILE` | OAuth client-secret path (default `client_secret.json`) |
| `TOKEN_FILE` | OAuth token cache path (default `token.json`) |
| `GOOGLE_API_KEY` | API key for key-authenticated endpoints |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | OAuth client credentials |
| `GOOGLE_URL`, `GOOGLE_SHEET_ID`, `GOOGLE_SHEET_NAME` | Sheet-specific identifiers |

## TOML configuration

Default scopes live in `assets/config/default.toml`. `find_default_config_path()`
locates it dynamically (relative to the package, then the project root, then the
CWD, including the `lib/googlepy/` submodule layout).

```toml
[google]
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

[google.scopes_by_service]
sheets = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

[oauth]
scopes = ["https://www.googleapis.com/auth/drive"]
```

Read values programmatically:

```python
from googlepy import get_default_config

get_default_config(["google", "scopes"])                        # global list
get_default_config(["google", "scopes_by_service", "sheets"])   # per service
```

See the [Config API reference](api/config.md) for full signatures.
