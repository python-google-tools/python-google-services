# CLAUDE.md — python-google-services

Guidance for Claude Code (and any contributor) working in this repository.

## What this repo is

`python-google-services` is a **reusable, app-agnostic** Google API service
library. It provides authentication (service account + OAuth) and authorized
service clients (Sheets, Drive). It must **not** contain product-specific logic,
caching, or persistence — those belong in the consuming applications
(e.g. `gspreadctl`).

## Project layout

```
assets/config/default.toml  # Default scopes (global + per-service)
src/
├── googlepy/               # Canonical package
│   ├── auth/               # Credential construction (service account, OAuth), scopes
│   ├── client/             # AuthorizedSession, GoogleServiceClient, factories
│   ├── config/             # Dynamic TOML & env configuration
│   ├── functional/         # Protocols, retry decorator, combinators, pagination
│   ├── services/           # Reusable stateless logic: sheets, drive, docs, gmail, calendar
│   └── exceptions.py       # GooglePyError, GoogleAPIError, ConfigurationError
├── client/                 # Backward-compatibility wrapper
├── config/                 # Backward-compatibility wrapper
└── sheet/                  # Backward-compatibility wrapper
tests/                      # Submodule test suite covering all modules & edge cases
__init__.py
```

## Design rules

- Keep the library **stateless**. No SQLite, no local caches, no CLI.
- Auth must support **both** service-account keys and OAuth user-consent.
- Scopes come from configuration (env var / `config/env.toml`), never hardcoded
  at call sites.
- Public functions return authorized clients/credentials — callers decide how to
  use them.

## Coding standards

These apply to **all** code in `auth/`, `config/`, `sheet/`, and `client/`.

### Functional, dynamic, reusable

- **Prefer a functional style.** Favor pure functions, explicit inputs/outputs,
  and immutability over stateful objects and side effects. Avoid hidden globals;
  pass dependencies (paths, scopes, credentials) in as arguments with sensible
  defaults resolved from config.
- **Logic must be dynamic.** This repo is consumed as a **git submodule across
  multiple projects**, so nothing may assume a fixed location or host layout:
  - Resolve file paths relative to the package (`Path(__file__).parent`), never
    hardcoded project paths (e.g. not `lib/googlepy/asserts/config/default.toml`).
  - Use package-relative imports so modules resolve regardless of the host
    project's `sys.path`.
  - Drive behavior from configuration (env vars / `config/*.toml`), not literals
    at call sites.

### Prefer established libraries over custom code

- **Before writing a custom helper or package, suggest a well-maintained,
  suitable Python library** for the scenario and prefer it (e.g. `gspread`,
  `google-auth`, `google-auth-oauthlib`, `pydantic`, `python-dotenv`,
  `pydantic-settings`, `tomllib`/`tomli`). Only write bespoke code when no
  established library fits — and say why.

### Modern Python & readability

- Use **advanced, idiomatic Python** where it improves clarity: type hints,
  `dataclasses`/`pydantic` models, `enum.Enum`, `pathlib`, context managers,
  generators/comprehensions, `functools` (e.g. `cache`, `partial`), structural
  pattern matching.
- **Every public function/class has a correct, complete docstring** — purpose,
  `Args`, `Returns`, and `Raises`. Keep docstrings in sync with the signature;
  an inaccurate docstring is a bug.
- **Modular structure.** One responsibility per module; small, composable
  functions. Split a module when it grows more than one concern.

### No dead code

- **No dead code.** No unused imports, variables, functions, parameters, or
  commented-out blocks. No stray scratch files (`test_file.txt`,
  throwaway scripts) committed to the repo. Remove it in the same change.

## ⚠️ MANDATORY: test-driven development (TDD)

**This project follows a test-driven architecture. Write the test first, watch
it fail, then write the code that makes it pass.** No production code is added or
changed without a test that covers it.

Tests live in a dedicated submodule:

```
tests/  →  git@github.com:python-google-tools/tests-python-google-services.git
```

### The TDD cycle (Red → Green → Refactor)

1. **Red** — add/extend a test in `tests/` that expresses the desired behavior;
   run it and confirm it **fails** for the right reason.
2. **Green** — write the minimum code in this repo to make the test pass.
3. **Refactor** — clean up code and tests while keeping the suite green.

### Rules

- Every public function/class in `auth/`, `config/`, `sheet/` has tests in
  `tests/`.
- **Every new function ships with unit tests that cover its edge cases** — not
  just the happy path: empty/`None` inputs, missing env vars/files, invalid
  config, wrong client type, and error/`raises` branches.
- A change is **not complete** until the full suite passes: `pytest`.
- Bug fixes start with a **failing regression test** that reproduces the bug.
- External Google APIs are **mocked** in unit tests — no live network calls in
  the default suite (keeps it fast, deterministic, and credential-free).
- Since `tests/` is a submodule (a separate repo), commit and push **both** this
  repo and `tests/` when a change spans them:

  ```bash
  # tests submodule first
  cd tests && git add -A && git commit -m "test: <behavior>" && git push origin main && cd ..
  # then the library (records the new tests pointer)
  git add -A && git commit -m "feat: <change>" && git push origin main
  ```

- Update the submodule pointer in this repo so the library always references the
  matching test revision.

## ⚠️ MANDATORY: keep the docs site in sync with every change

**The docs site is the source of truth for documentation. Every code or
behavior change in this repo MUST be accompanied by a matching docs update in
the same work session.** Do not consider a change complete until the docs
reflect it.

Docs are built with **MkDocs + Material + mkdocstrings** and deployed to
**GitHub Pages**. They live **in this repo** under `docs/`, so documentation is
versioned with the code and reviewed in the same PR — there is no separate wiki
repo to push.

```
docs/
├── index.md            # Home — overview, install-as-submodule, quick start
├── authentication.md   # Service account / OAuth / API key
├── configuration.md    # Scopes (env var / TOML), env vars, secret files
├── architecture.md     # Layered design + UML (Mermaid + auto-generated)
├── api/                # API reference — rendered from docstrings via mkdocstrings
└── diagrams/           # UML diagrams generated by scripts/gen_uml.py (do not hand-edit)
mkdocs.yml              # Site config (nav, theme, plugins)
scripts/gen_uml.py      # Regenerates UML class/package diagrams via pyreverse
.github/workflows/docs.yml  # Builds with --strict and deploys to Pages
```

### Local preview

```bash
pip install -e ".[docs]"     # mkdocs-material, mkdocstrings[python], pylint
python scripts/gen_uml.py    # regenerate UML from source
mkdocs serve                 # live preview at http://127.0.0.1:8000
```

### On every change — required workflow

1. Make the code change in this repo.
2. Update the matching docs:
   - New/changed public function or class → it appears automatically in the
     `api/` reference **via its docstring**, so keep the docstring correct and
     complete (this is also a coding-standards rule above).
   - New auth mode, scope, or config option → update `authentication.md` /
     `configuration.md`.
   - New/changed module or relationship → update `architecture.md` and
     regenerate diagrams: `python scripts/gen_uml.py`.
   - Behavior or breaking change → note it on the relevant page.
   - Keep `index.md` (overview/index) current.
3. Verify the site builds cleanly — the CI uses the same command:

   ```bash
   mkdocs build --strict
   ```

4. Commit docs alongside the code change (same branch/PR), typed `docs:`:

   ```bash
   git add -A && git commit -m "docs: sync docs for <change>"
   ```

5. A change is **not done** until `mkdocs build --strict` passes and the docs
   commit is included. Deployment to Pages happens automatically on merge to
   `main` via `.github/workflows/docs.yml`.

### What each page should cover

- **index** — overview, install-as-submodule, quick start, page index.
- **authentication** — service account vs OAuth vs API key, obtaining credentials.
- **configuration** — scope resolution order, env vars, TOML config.
- **architecture** — layered design and UML diagrams (kept in lockstep via `pyreverse`).
- **api/** — every public module/function, rendered from docstrings.

## Git workflow & commit conventions

**Every change follows a correct branch strategy and uses accurate Conventional
Commits.** Do not commit straight to `main`.

### Branching

- Branch off `main`, one branch per logical change, named by type:
  - `feat/<slug>`, `fix/<slug>`, `refactor/<slug>`, `ci/<slug>`,
    `chore/<slug>`, `docs/<slug>`.
- Open a PR into `main`; keep branches small and focused.

### Conventional Commits

Pick the type that matches what the change actually does:

- `feat:` — new user-facing capability.
- `fix:` — bug fix (paired with a regression test).
- `refactor:` — behavior-preserving restructuring (no API change).
- `ci:` — CI/pipeline/workflow changes.
- `chore:` — tooling, deps, packaging, housekeeping.
- `test:` — adding or changing tests in the `tests/` submodule.
- `docs:` — documentation, including all `docs/` site updates.

A single change may produce multiple commits (e.g. `test:` in the submodule,
`feat:` in the library, `docs:` for the `docs/` site) — each typed correctly.
