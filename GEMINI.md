# GEMINI.md — python-google-services (`googlepy`)

Context and guidelines for Google Gemini and AI contributors working in this repository.

---

## 1. What This Repository Is

`python-google-services` (`googlepy`) is a **reusable, framework-agnostic, and stateless** Google API service library for Python. It provides:
- **Unified Authentication**: Service account JSON keys, OAuth 2.0 user consent, and API keys.
- **Dynamic Scope Resolution**: Hierarchical resolution (`explicit args > GOOGLE_SCOPES env var > default.toml > built-in defaults`).
- **Resilient HTTP Clients**: Standardized `GoogleServiceClient` powered by `google.auth.transport.requests.AuthorizedSession` with automatic token refresh, exponential backoff, and full jitter.
- **Google Workspace Core Services**: Stateless helper modules for:
  - **Sheets** (via `gspread`)
  - **Drive** (Drive API v3)
  - **Docs** (Docs API v1)
  - **Gmail** (Gmail API v1)
  - **Calendar** (Calendar API v3)

### Core Invariant
This library is intentionally **stateless and app-agnostic**: it holds no product-specific business logic, no local databases (SQLite), and no CLI tools. Those belong exclusively in consuming applications (e.g. `gspreadctl`).

---

## 2. Project Layout

```
python-google-services/
├── assets/
│   └── config/
│       └── default.toml          # Canonical default scopes (global & per-service)
├── asserts/
│   └── config/
│       └── default.toml          # Backward-compatibility alias
├── src/
│   ├── googlepy/                 # Canonical library package
│   │   ├── __init__.py           # Top-level unified exports
│   │   ├── exceptions.py         # GooglePyError, GoogleAPIError, ConfigurationError
│   │   ├── auth/                 # Credential providers and scope resolution
│   │   │   ├── __init__.py
│   │   │   ├── models.py         # Pydantic input validation models
│   │   │   ├── provider.py       # Zero-argument closures & client_factory
│   │   │   └── scopes.py         # Scope resolution hierarchy
│   │   ├── client/               # HTTP client sessions and service builders
│   │   │   ├── __init__.py
│   │   │   ├── base.py           # GoogleServiceClient, GoogleClientType
│   │   │   ├── factory.py        # Dynamic get_service_client builder
│   │   │   ├── sheet.py          # gspread client helpers
│   │   │   ├── drive.py          # Drive v3 client factory
│   │   │   ├── docs.py           # Docs v1 client factory
│   │   │   ├── gmail.py          # Gmail v1 client factory
│   │   │   └── calendar.py       # Calendar v3 client factory
│   │   ├── config/               # Dynamic configuration
│   │   │   ├── __init__.py
│   │   │   ├── default.py        # Dynamic pathlib TOML locator
│   │   │   └── env.py            # Environment variable loading
│   │   ├── functional/           # Functional programming primitives
│   │   │   ├── __init__.py
│   │   │   ├── combinators.py    # pipe, compose, curry
│   │   │   ├── decorators.py     # retry_with_backoff, memoize_with_ttl
│   │   │   ├── pagination.py     # Lazy paginate generator
│   │   │   └── protocols.py      # Structural subtyping protocols (PEP 544)
│   │   └── services/             # Pure stateless Google Workspace service operations
│   │       ├── __init__.py
│   │       ├── sheets.py         # Spreadsheets & worksheets
│   │       ├── drive.py          # Files, folders, uploads, permissions
│   │       ├── docs.py           # Docs text extraction, insertion, batch replace
│   │       ├── gmail.py          # Messages, drafts, labels
│   │       └── calendar.py       # Events & calendar management
│   ├── client/                   # Backward-compatibility wrapper
│   ├── config/                   # Backward-compatibility wrapper
│   └── sheet/                    # Backward-compatibility wrapper
├── tests/                        # Dedicated test submodule
│   ├── test_auth.py
│   ├── test_calendar_service.py
│   ├── test_client.py
│   ├── test_config.py
│   ├── test_docs_service.py
│   ├── test_drive_service.py
│   ├── test_edge_cases.py
│   ├── test_functional.py
│   ├── test_gmail_service.py
│   └── test_sheets_service.py
├── .env.example
├── pyproject.toml
├── README.md
├── CLAUDE.md
└── AGENTS.md
```

---

## 3. Core Architectural Rules

### 3.1 Functional Style & Immutability
- Favor pure functions: all dependencies (clients, credentials, paths) must be explicitly passed as parameters with sensible defaults resolved from configuration.
- Use **zero-argument closure providers** (`service_account_provider`, `oauth_provider`, `api_key_provider`). Defer all network and disk I/O until the closure is invoked.
- Use `client_factory(credentials_provider, verify=...)` to lazily instantiate and cache clients.

### 3.2 Dynamic Multi-Project Reusability
This repository is consumed as a **git submodule across multiple external projects** (e.g. at `lib/googlepy`) as well as an installable package:
- **Never hardcode relative paths** like `lib/googlepy/...` or `C:/...`.
- Resolve files dynamically relative to the module using `pathlib.Path(__file__).resolve()`.
- Use package-relative imports (`from googlepy.auth import ...`).
- Drive configuration from `.env` or `assets/config/default.toml` with graceful fallback to `asserts/config/default.toml`.

### 3.3 Prefer Established Libraries Over Custom Code
Do not write custom reinvented wheels when standard libraries exist:
- **Google Sheets**: `gspread`
- **Authentication**: `google-auth`, `google-auth-oauthlib`
- **Validation**: `pydantic`
- **HTTP Engine**: `google.auth.transport.requests.AuthorizedSession` / `requests`
- **Declarative Retries**: `tenacity` (recommended for production host apps)
- **Advanced Environment**: `pydantic-settings` (recommended for consuming apps)
- **Dynamic API Discovery**: `google-api-python-client`

### 3.4 Resilient API Operations
- Use `@retry_with_backoff` on transient Google API errors (HTTP 429 Too Many Requests, 500, 502, 503 Service Unavailable).
- Use exponential backoff with full randomized jitter to prevent thundering herds.

### 3.5 Memory-Efficient Streaming
- Never load unbounded API lists into memory.
- Use the `paginate` generator or service stream helpers (`iter_files`, `iter_messages`, `iter_events`) to stream items lazily across pages using `pageToken` and `nextPageToken`.

### 3.6 Zero Dead Code
- No unused imports, uncalled functions, commented-out blocks, or temporary scratch files.
- Every line of code must be active and tested.

---

## 4. Coding Standards

- **Python Version**: `>=3.9`.
- **Typing**: Use static typing everywhere (`typing.Sequence`, `Mapping`, `Optional`, `TypeVar`, PEP 544 `Protocol`).
- **Docstrings**: Every public class, function, and module must have a complete Google/Sphinx style docstring with `Args`, `Returns`, `Raises`, and `Example`.

---

## 5. Mandatory Test-Driven Development (TDD)

All development in this repository strictly enforces **Test-Driven Development**:

1. **Red**: Write or update a unit test in `tests/` expressing the expected behavior or reproducing a bug. Run pytest and verify it **fails** for the expected reason.
2. **Green**: Write the minimum code in `src/` to make the test pass.
3. **Refactor**: Clean up implementation and tests while keeping the suite green.

### Testing Rules
- **Mock All External Google APIs**: Zero live network calls during unit tests. Unit tests must be fast, deterministic, and credential-free.
- **Edge Cases Are Mandatory**:
  - Empty or whitespace-only inputs.
  - Missing environment variables and missing credential files.
  - Rate limiting (429) recovery and non-retryable 4xx errors.
  - HTTP 204 No Content and non-JSON HTML error bodies.
  - Pagination boundary conditions (`max_items=0`, empty pages, missing next tokens).
  - Out-of-bounds indices and duplicate creation attempts.
- Run tests via pytest:
  ```bash
  pytest -v
  ```

### Submodule Commit Protocol
Since `tests/` is a git submodule (a separate repository), commit both when making changes:
```bash
# 1. Commit and push the tests submodule first
cd tests && git add -A && git commit -m "test: <description>" && git push origin main && cd ..

# 2. Commit and push the library repo (updates submodule pointer)
git add -A && git commit -m "feat: <description>" && git push origin main
```

---

## 6. Git Workflow & Conventional Commits

Never commit directly to `main`. Always branch off `main` with a typed branch name:

### Branch Naming
- `feat/<feature-name>`
- `fix/<bug-name>`
- `refactor/<name>`
- `test/<name>`
- `docs/<name>`
- `chore/<name>`

### Conventional Commit Types
- `feat:` — New user-facing capability.
- `fix:` — Bug fix paired with regression test.
- `refactor:` — Code restructuring with no behavior change.
- `test:` — Adding or updating test cases in `tests/`.
- `docs:` — Documentation changes in `README.md`, `CLAUDE.md`, or `GEMINI.md`.
- `chore:` — Dependencies, configuration, or packaging changes.
- `ci:` — CI workflow updates.

---

## 7. Wiki Synchronization

Every public API change, new service helper, or configuration option **must** be reflected in the wiki repository (`git@github.com:ThanuMahee12/python-google-services.wiki.git`):
- New/modified functions → update API reference page.
- New configuration or auth mode → update setup/configuration page.
- Keep `Home.md` current.
