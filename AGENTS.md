# AGENTS.md — Autonomous Coding Agent Guidelines

Operational instructions and architectural constraints for autonomous AI coding agents working in `python-google-services` (`googlepy`).

---

## 1. Project Purpose & Scope

`python-google-services` (`googlepy`) provides shared, stateless building blocks for authenticating with Google APIs and interacting with Google Workspace Core services (**Sheets**, **Drive**, **Docs**, **Gmail**, **Calendar**).

### Core Boundaries
- **Stateless Library**: No local databases, no file-based caching, no CLI commands, and no product-specific business logic.
- **Consumer Independence**: The library is consumed as a Git submodule (e.g. `lib/googlepy`) or standard dependency. It must never assume a fixed host directory structure.

---

## 2. Environment & Tooling

- **Python**: `>=3.9`
- **Package Manager**: `uv` or `pip`
- **Build Backend**: `hatchling`
- **Test Runner**: `pytest`
- **Primary Dependencies**:
  - `gspread` (Google Sheets)
  - `google-auth`, `google-auth-oauthlib` (Authentication & Tokens)
  - `requests` (HTTP transport)
  - `pydantic` (Data and input validation)
  - `python-dotenv` (Environment variable loading)

### Test Execution Command
Run the test suite using pytest without caching issues:
```bash
pytest -p no:cacheprovider -v
```

---

## 3. Architectural Rules for Agents

### 3.1 Functional Programming Style
1. **Zero-Argument Closures for Auth**:
   All credential providers (`service_account_provider`, `oauth_provider`, `api_key_provider`) return zero-argument callables `Callable[[], Credentials]`. Never execute disk I/O or token requests upon provider declaration.
2. **Client Factory Closure**:
   Use `client_factory(credentials_provider, verify=...)` to lazily construct and cache client instances.
3. **Pure Service Functions**:
   Functions in `googlepy.services` (`sheets`, `drive`, `docs`, `gmail`, `calendar`) must be pure and stateless. They accept `(client, ...)` and return Python dictionaries, lists, or primitive types.

### 3.2 Dynamic Path Resolution
- **Forbidden**: Hardcoded paths such as `lib/googlepy/asserts/...` or absolute system paths.
- **Required**: Resolve paths dynamically using `pathlib.Path(__file__).resolve()` as demonstrated in `googlepy.config.default`.

### 3.3 Transient Error Handling & Backoff
- All Google REST API calls must handle transient HTTP status codes (`429`, `500`, `502`, `503`, `504`) using exponential backoff with full randomized jitter via `@retry_with_backoff`.
- Non-transient errors (`400`, `401`, `403`, `404`) must fail immediately by raising `GoogleAPIError`.

### 3.4 Lazy Stream Pagination
- Use `googlepy.functional.pagination.paginate` or generator helpers (`iter_files`, `iter_messages`, `iter_events`) when listing resources to stream records lazily across pages via `pageToken`.

### 3.5 Established Libraries
- Always prefer established, maintained libraries over bespoke logic:
  - `gspread` for Google Sheets.
  - `google-auth` for token refresh and service accounts.
  - `pydantic` for schema validation.
  - `tenacity` for production-grade retries in consuming applications.
  - `pydantic-settings` for typed configuration in consuming applications.

### 3.6 Zero Dead Code Policy
- Never leave unused imports, unreferenced variables, dead functions, or scratch files (`test_file.txt`, `temp.py`).

---

## 4. Test-Driven Development (TDD) Mandate

Every code change must adhere to strict TDD:
1. **Red**: Write a failing unit test in `tests/` covering the intended behavior or edge case.
2. **Green**: Write the minimal implementation code in `src/googlepy/` to pass the test.
3. **Refactor**: Clean up and optimize while keeping all tests green.

### Mocking Requirement
- **Zero Live Network Calls**: All external Google HTTP endpoints and `gspread` clients must be mocked in unit tests.
- **Edge Cases Must Be Covered**:
  - Missing or malformed configuration files.
  - Empty or whitespace-only strings.
  - Rate-limit recovery and retry exhaustion.
  - HTTP 204 No Content empty bodies.
  - Non-JSON HTML error responses.
  - Pagination boundary limits (`max_items=0`, empty result lists).
  - Out-of-bounds indices and duplicate resource errors.

---

## 5. Git Commit Protocol

Follow Conventional Commits strictly:
- `feat:` — New capabilities or service methods.
- `fix:` — Bug fixes (must include a regression test).
- `refactor:` — Code restructuring with no external behavior changes.
- `test:` — Adding or modifying unit tests in `tests/`.
- `docs:` — Documentation updates (`README.md`, `CLAUDE.md`, `GEMINI.md`, `AGENTS.md`).
- `chore:` — Dependency updates, packaging, or housekeeping.

### Submodule Handling
Because `tests/` is a separate git submodule:
1. Commit and push the `tests/` submodule first:
   ```bash
   cd tests && git add -A && git commit -m "test: <description>" && git push origin main && cd ..
   ```
2. Commit and push the main library:
   ```bash
   git add -A && git commit -m "feat: <description>" && git push origin main
   ```
