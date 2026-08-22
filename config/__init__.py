"""Configuration loading for googlepy.

The canonical defaults (scopes, OAuth secret/token files) live in
``default.toml`` next to this module. These helpers read it so defaults are
managed in one place rather than hardcoded across the codebase.
"""

from pathlib import Path

try:  # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # Python 3.9 / 3.10
    import tomli as tomllib

DEFAULT_CONFIG_PATH = Path(__file__).with_name("default.toml")


def load_config(path=None):
    """Load and parse the TOML config; return ``{}`` if the file is absent."""
    p = Path(path) if path else DEFAULT_CONFIG_PATH
    if not p.is_file():
        return {}
    with open(p, "rb") as fh:
        return tomllib.load(fh)


def config_scopes(path=None):
    """Return the ``[google].scopes`` list from config (empty list if unset)."""
    return list(load_config(path).get("google", {}).get("scopes", []))


def config_secret_file(path=None):
    """Return ``[google].secret_file`` from config (``None`` if unset)."""
    return load_config(path).get("google", {}).get("secret_file")


def config_token_file(path=None):
    """Return ``[google].token_file`` from config (``None`` if unset)."""
    return load_config(path).get("google", {}).get("token_file")
