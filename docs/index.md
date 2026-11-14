# python-google-services

Reusable, framework-agnostic **Google API service utilities for Python** —
authentication and authorized service clients (Sheets, Drive, Docs, Gmail,
Calendar), with nothing app-specific mixed in.

This library is designed to be consumed as a **git submodule** by higher-level
tools. It stays **stateless and app-agnostic**: no caching, no persistence, no
CLI — it knows only about Google.

---

## What it provides

- **Auth** — build authorized credentials from a **service account key**, an
  **OAuth user-consent** flow, or an **API key**.
- **Scopes** — centralized, per-service scope configuration via env var or
  `assets/config/default.toml`.
- **Service clients** — factory helpers returning authorized Google API clients.
- **Functional primitives** — composable retry, memoization, pagination, and
  pipe/compose/curry combinators.
- **Stateless services** — reusable logic for Sheets, Drive, Docs, Gmail, and
  Calendar.

## Quick start

Add it to your project as a submodule:

```bash
git submodule add git@github.com:python-google-tools/python-google-services.git lib/googlepy
git submodule update --init --recursive
```

Configure scopes (env var):

```bash
GOOGLE_SCOPES=https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/drive
```

Use it:

```python
from googlepy import get_sheets_client

client = get_sheets_client()
sheet = client.open_by_key("your-sheet-id")
```

## Documentation

| Page | Contents |
|------|----------|
| [Authentication](authentication.md) | Service account, OAuth, API key — obtaining credentials |
| [Configuration](configuration.md) | Scopes (env var / TOML), secret files, env vars |
| [Architecture](architecture.md) | Layered design with UML class & sequence diagrams |
| [API Reference](api/auth.md) | Public modules & functions, generated from docstrings |

## Design principles

- **Stateless** — no SQLite, no local caches, no CLI.
- **All auth modes** — service-account keys, OAuth user-consent, API keys.
- **Config-driven scopes** — never hardcoded at call sites.
- **Dynamic** — paths resolve relative to the package, so the submodule works at
  any location in any host project.
- **Return, don't decide** — functions return authorized clients; callers choose
  how to use them.

## License

MIT
