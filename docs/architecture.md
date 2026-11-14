# Architecture

`googlepy` is organized in layers. Higher layers depend only on lower ones, and
every layer is **stateless** — state (caching, persistence) belongs to the
consuming application.

## Layered design

```mermaid
flowchart TD
    subgraph services["services/ — stateless reusable logic"]
        S1[sheets] & S2[drive] & S3[docs] & S4[gmail] & S5[calendar]
    end
    subgraph client["client/ — authorized clients & factories"]
        C1[GoogleServiceClient] & C2[factory]
    end
    subgraph auth["auth/ — credentials & scopes"]
        A1[provider] & A2[models] & A3[scopes]
    end
    subgraph functional["functional/ — composable primitives"]
        F1[decorators] & F2[combinators] & F3[pagination] & F4[protocols]
    end
    subgraph config["config/ — dynamic env & TOML"]
        G1[env] & G2[default]
    end

    services --> client --> auth --> config
    client -.uses.-> functional
    auth -.uses.-> functional
```

## Core class relationships

```mermaid
classDiagram
    class ServiceAccountAuth {
        +str key_file
        +dict key_info
    }
    class OAuthAuth {
        +str client_secret_file
        +str token_file
    }
    class ApiKeyAuth {
        +str api_key
    }
    class GoogleServiceClient {
        +AuthorizedSession session
        +request(method, url)
    }
    class CredentialsProvider {
        <<Protocol>>
        +__call__() Credentials
    }

    CredentialsProvider <|.. ServiceAccountAuth
    CredentialsProvider <|.. OAuthAuth
    GoogleServiceClient --> CredentialsProvider : built from
```

## Authentication flow

```mermaid
sequenceDiagram
    participant App as Host app
    participant F as client_factory
    participant P as credentials_provider
    participant G as Google API

    App->>F: get_client()
    F->>P: provider()  (first call only)
    P->>P: resolve_scopes()
    P-->>F: Credentials
    F->>G: gspread.authorize(creds)
    G-->>F: authorized client
    F-->>App: cached client
    App->>F: get_client()  (later)
    F-->>App: same cached client
```

## Auto-generated class diagram

The diagram below is generated directly from the source with
[`pyreverse`](https://pylint.readthedocs.io/en/latest/pyreverse.html) (ships with
`pylint`), so it never drifts from the code. Regenerate it with:

```bash
python scripts/gen_uml.py
```

--8<-- "docs/diagrams/classes.md"
