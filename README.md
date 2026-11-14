# python-google-services (`googlepy`)

Reusable, framework-agnostic Google API service utilities for Python.

This library provides shared building blocks for authenticating with Google APIs, managing scopes dynamically, and interacting with Google Workspace assets (**Sheets**, **Drive**, **Docs**, **Gmail**, **Calendar**) using **pure functional programming**, **stateless service modules**, and **advanced Python patterns**.

It is designed to be consumed either as a **standalone Python package** or as a **git submodule** (e.g. at `lib/googlepy`) across multiple host projects, with **zero hardcoded paths** and no product-specific state.

---

## Key Capabilities

- **Unified Authentication (`googlepy.auth`)**:
  - Pure closure-based providers for **Service Accounts**, **OAuth 2.0 User Consent**, and **API Keys**.
  - Deferred, lazy evaluation: network and disk I/O occur only when credentials are requested.
  - Cached client factory closure with optional connectivity verification.
- **Dynamic Configuration & Scopes (`googlepy.config`)**:
  - Hierarchical scope resolution: `explicit arguments > GOOGLE_SCOPES env var > default.toml > built-in defaults`.
  - Service-specific scopes for Sheets, Drive, Docs, Gmail, and Calendar.
  - Dynamic path resolution via `pathlib.Path`: automatically locates `assets/config/default.toml` regardless of the host project's directory structure (with backwards-compatible fallback to `asserts/`).
- **Core HTTP Client & Factory (`googlepy.client`)**:
  - `GoogleServiceClient` powered by `google.auth.transport.requests.AuthorizedSession`.
  - Automatic Bearer token injection and seamless token refresh.
  - Structured error translation with `GoogleAPIError` (captures HTTP status code, API error message, and JSON error details).
  - Dynamic factory `get_service_client(service_name, ...)` supporting all Google Workspace services.
- **High-Level Stateless Services (`googlepy.services`)**:
  - **Sheets**: `get_spreadsheet`, `read_range`, `write_range`, `append_rows`, `list_worksheets`, `create_worksheet`, `delete_worksheet`, `clear_worksheet`.
  - **Drive**: `list_files`, `iter_files`, `find_file_by_name`, `create_folder`, `upload_file`, `download_file`, `delete_file`, `share_file`.
  - **Docs**: `create_document`, `get_document`, `get_document_text`, `insert_text`, `replace_all_text`.
  - **Gmail**: `send_message`, `create_draft`, `list_messages`, `iter_messages`, `get_message`, `list_labels`.
  - **Calendar**: `list_events`, `iter_events`, `create_event`, `get_event`, `delete_event`, `list_calendars`.
- **Functional Programming Primitives (`googlepy.functional`)**:
  - `@retry_with_backoff`: Higher-order decorator implementing exponential backoff with full jitter on transient HTTP errors (429, 500, 502, 503, 504).
  - `@memoize_with_ttl`: Closure-based memoization with time-to-live expiration.
  - `paginate`: Pure generator yielding items lazily across paginated Google REST endpoints without buffering entire result sets in memory.
  - `pipe`, `compose`, `curry`: Combinators for assembling declarative transformation pipelines.
  - Type protocols (PEP 544): `CredentialsProvider`, `HTTPClientProtocol`, `ServiceClientProtocol`.

---

## Recommended Libraries for this Scenario

Rather than building complex bespoke infrastructure from scratch, `googlepy` integrates and recommends established, high-quality libraries:

| Capability | Recommended Library | Purpose in this Architecture |
|---|---|---|
| **Google Sheets Interaction** | [`gspread`](https://github.com/burnash/gspread) | Pythonic, battle-tested API wrapper for Google Sheets v4. |
| **Authentication & Tokens** | [`google-auth`](https://github.com/googleapis/google-auth-library-python) & [`google-auth-oauthlib`](https://github.com/googleapis/google-auth-library-python-oauthlib) | Official Google library for service accounts and OAuth consent flows. |
| **Data Validation** | [`pydantic`](https://github.com/pydantic/pydantic) | Runtime type validation for API keys, service key paths, and OAuth secrets. |
| **Declarative Retries** | [`tenacity`](https://github.com/jd/tenacity) | Recommended for advanced production retries with customizable retry conditions and statistics. |
| **Environment Settings** | [`pydantic-settings`](https://github.com/pydantic/pydantic-settings) | Recommended when host applications require typed, schema-driven environment variables. |
| **Generic API Discovery** | [`google-api-python-client`](https://github.com/googleapis/google-api-python-client) | Official Google SDK for dynamic runtime discovery of any Google REST API. |

---

## Project Layout

```
python-google-services/
├── assets/
│   └── config/
│       └── default.toml          # Default global and per-service Google scopes
├── asserts/
│   └── config/
│       └── default.toml          # Backward-compatibility alias
├── src/
│   ├── googlepy/                 # Primary canonical package
│   │   ├── __init__.py           # Unified top-level package exports
│   │   ├── exceptions.py         # GooglePyError, GoogleAPIError, ConfigurationError
│   │   ├── auth/                 # Credential providers and scope resolution
│   │   │   ├── __init__.py
│   │   │   ├── models.py         # Pydantic input validation models
│   │   │   ├── provider.py       # Closure-based providers (service account, OAuth, API key)
│   │   │   └── scopes.py         # Scope resolution hierarchy
│   │   ├── client/               # HTTP client sessions and service builders
│   │   │   ├── __init__.py
│   │   │   ├── base.py           # GoogleServiceClient, GoogleClientType
│   │   │   ├── factory.py        # Dynamic get_service_client factory
│   │   │   ├── sheet.py          # gspread client helpers
│   │   │   ├── drive.py          # Drive v3 client factory
│   │   │   ├── docs.py           # Docs v1 client factory
│   │   │   ├── gmail.py          # Gmail v1 client factory
│   │   │   └── calendar.py       # Calendar v3 client factory
│   │   ├── config/               # Dynamic configuration
│   │   │   ├── __init__.py
│   │   │   ├── default.py        # Dynamic TOML locator (pathlib)
│   │   │   └── env.py            # Environment variable loading
│   │   ├── functional/           # Functional programming primitives
│   │   │   ├── __init__.py
│   │   │   ├── combinators.py    # pipe, compose, curry
│   │   │   ├── decorators.py     # retry_with_backoff, memoize_with_ttl
│   │   │   ├── pagination.py     # Lazy paginate generator
│   │   │   └── protocols.py      # Structural subtyping protocols (PEP 544)
│   │   └── services/             # Pure stateless Google Workspace service operations
│   │       ├── __init__.py
│   │       ├── sheets.py
│   │       ├── drive.py
│   │       ├── docs.py
│   │       ├── gmail.py
│   │       └── calendar.py
│   ├── client/                   # Backward-compatibility wrapper
│   ├── config/                   # Backward-compatibility wrapper
│   └── sheet/                    # Backward-compatibility wrapper
├── tests/                        # Submodule test suite covering happy paths and edge cases
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
└── README.md
```

---

## Installation

### As a standard dependency:
```bash
pip install -e .
# or with uv
uv pip install -e .
```

### As a Git Submodule:
```bash
git submodule add git@github.com:ThanuMahee12/python-google-services.git lib/googlepy
git submodule update --init --recursive
```

---

## Quickstart & Usage

### 1. Google Sheets (`gspread`)
```python
from googlepy.client.sheet import get_sheets_client
from googlepy.services import sheets

# Authenticate via service account
client = get_sheets_client(service_key_file="service_key.json")

# Open spreadsheet and read/write values
doc = sheets.get_spreadsheet(client, id="YOUR_SPREADSHEET_ID")
sheet = sheets.get_worksheet(doc, 0)

# Write data
sheets.write_range(sheet, "A1:B1", [["Name", "Score"]])
sheets.append_rows(sheet, [["Alice", "95"], ["Bob", "88"]])

# Read data
records = sheets.get_all_records(sheet)
print(records)
```

### 2. Google Drive (Files & Folders)
```python
from googlepy.client import get_drive_client
from googlepy.services import drive

client = get_drive_client(service_key_file="service_key.json")

# Create a folder
folder = drive.create_folder(client, folder_name="Reports")

# Upload a file
file_obj = drive.upload_file(
    client,
    name="summary.txt",
    content="Monthly Report Content",
    mime_type="text/plain",
    parent_id=folder["id"],
)

# Lazy pagination over all files
for file in drive.iter_files(client, query="trashed = false", page_size=50):
    print(file["name"], file["id"])
```

### 3. Google Docs
```python
from googlepy.client import get_docs_client
from googlepy.services import docs

client = get_docs_client(service_key_file="service_key.json")

# Create and populate a document
new_doc = docs.create_document(client, title="Sprint Review")
doc_id = new_doc["documentId"]

docs.insert_text(client, doc_id, text="Sprint 42 completed successfully.\n", index=1)
docs.replace_all_text(client, doc_id, target_text="Sprint 42", replacement_text="Sprint 43")

# Extract full plain text
content = docs.get_document_text(client, doc_id)
print(content)
```

### 4. Gmail (Send & Search)
```python
from googlepy.client import get_gmail_client
from googlepy.services import gmail

# Using OAuth user consent
client = get_gmail_client(client_type="OAUTH2")

# Send email
gmail.send_message(
    client,
    to="team@example.com",
    subject="Weekly Update",
    body="<h1>Weekly Status</h1><p>All tasks on track.</p>",
    html=True,
)

# Iterate over matching messages
for msg in gmail.iter_messages(client, query="is:unread", max_items=10):
    print("Unread Message ID:", msg["id"])
```

### 5. Google Calendar (Events)
```python
from googlepy.client import get_calendar_client
from googlepy.services import calendar

client = get_calendar_client(service_key_file="service_key.json")

# Create an event
event = calendar.create_event(
    client,
    summary="Project Planning",
    start_time="2026-11-20T10:00:00Z",
    end_time="2026-11-20T11:00:00Z",
    description="Q4 roadmap review",
    location="Conference Room 1",
)

# List upcoming events
events = calendar.list_events(client, time_min="2026-11-01T00:00:00Z", max_results=10)
for ev in events:
    print(ev["summary"], ev["start"])
```

### 6. Functional Composition & Pipelines
```python
from googlepy.functional import pipe, compose, curry

# Composition pipeline
clean_scopes = pipe(
    "  https://example.com/s1,  https://example.com/s2  ",
    lambda s: s.split(","),
    lambda lst: [item.strip() for item in lst],
    tuple,
)
```

---

## Testing

This project enforces strict **Test-Driven Development (TDD)**. All unit tests mock external Google APIs, ensuring fast, deterministic, credential-free verification.

Run the test suite:
```bash
pytest -v
```

The test suite covers:
- Credential construction and closures (`service_account_provider`, `oauth_provider`, `client_factory`).
- Hierarchical scope resolution and environment overrides.
- HTTP client methods, retry with backoff on transient errors (429/500/503), and error parsing.
- Service operations across Sheets, Drive, Docs, Gmail, and Calendar.
- Edge cases: whitespace trimming, out-of-bounds indices, missing files, 204 No Content responses, and pagination boundaries.

---

## License

MIT
