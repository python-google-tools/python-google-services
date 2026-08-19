# python-google-services

Reusable, framework-agnostic Google API service utilities for Python.

This library provides the shared building blocks for authenticating with Google
APIs and obtaining ready-to-use service clients. It is consumed as a git
submodule by higher-level tools (for example, `gspreadctl`), but has no
dependency on any of them — it knows only about Google.

## What it provides

- **Auth** — build authorized credentials from either a **service account key**
  or an **OAuth user-consent** flow.
- **Scopes** — centralized scope configuration (env var, TOML, or defaults).
- **Service clients** — factory helpers that return authorized Google API
  clients (Sheets, Drive).

The library is intentionally **stateless and app-agnostic**: it performs no
caching, no persistence, and holds no product-specific logic.

## Layout

```
python-google-services/
├── auth/            # credential construction (service account, OAuth)
│   └── auth.py
├── config/          # scope + secret configuration
│   ├── env.py
│   └── env.toml
├── .env.example     # sample environment configuration
└── __init__.py
```

## Configuration

Scopes can be supplied via environment variable (see `.env.example`):

```bash
GOOGLE_SCOPES=https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/drive
```

or via `config/env.toml`:

```toml
[google]
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
secret_file = "client_secret.json"
```

## Installation (as a submodule)

```bash
git submodule add git@github.com:ThanuMahee12/python-google-services.git lib/googlepy
git submodule update --init --recursive
```

## Usage

```python
from googlepy.auth.auth import get_scopes

scopes = get_scopes()
```

> API surface is expanding — see the
> [project wiki](https://github.com/ThanuMahee12/python-google-services/wiki)
> for the full, always-current reference.

## Documentation

Full documentation lives in the **wiki**, which is kept in lockstep with the
code. See [CLAUDE.md](CLAUDE.md) for the contribution rule that enforces this.

## License

MIT
