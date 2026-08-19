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
auth/       # credential construction (service account, OAuth), scope resolution
config/     # scope + secret configuration (env.toml, env.py)
__init__.py
```

## Design rules

- Keep the library **stateless**. No SQLite, no local caches, no CLI.
- Auth must support **both** service-account keys and OAuth user-consent.
- Scopes come from configuration (env var / `config/env.toml`), never hardcoded
  at call sites.
- Public functions return authorized clients/credentials — callers decide how to
  use them.

## ⚠️ MANDATORY: keep the wiki in sync with every change

**The wiki is the source of truth for documentation. Every code or behavior
change in this repo MUST be accompanied by a matching wiki update in the same
work session.** Do not consider a change complete until the wiki reflects it.

Wiki repository (separate git repo):

```
git@github.com:ThanuMahee12/python-google-services.wiki.git
```

### One-time setup

Clone the wiki next to this repo (it is a distinct repository):

```bash
git clone git@github.com:ThanuMahee12/python-google-services.wiki.git
```

> The wiki repo only exists after at least one page has been created via the
> GitHub web UI (`.../wiki/_new`).

### On every change — required workflow

1. Make the code change in this repo.
2. Update the corresponding wiki page(s) in `python-google-services.wiki/`:
   - New/changed public function or class → update its reference page.
   - New auth mode, scope, or config option → update the setup/config page.
   - Behavior or breaking change → note it on the relevant page.
   - `Home.md` is the landing page; keep its overview/index current.
3. Commit **both** repositories:

   ```bash
   # code
   git add -A && git commit -m "feat: <change>"

   # wiki
   cd ../python-google-services.wiki
   git add -A && git commit -m "docs: sync wiki for <change>"
   git push origin master   # wiki default branch is 'master'
   ```

4. A change is **not done** until the wiki commit is pushed.

### What each wiki page should cover

- **Home** — overview, install-as-submodule, quick start, page index.
- **Authentication** — service account vs OAuth, how to obtain credentials.
- **Configuration** — scopes (env var / `env.toml`), secret file.
- **API Reference** — every public module/function with a short example.

## Commit conventions

Use Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `chore:`).
Wiki-sync commits use `docs:`.
