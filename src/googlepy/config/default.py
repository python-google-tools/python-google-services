from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def find_default_config_path(explicit_path: str | Path | None = None) -> Path:
    """Find the default TOML configuration path dynamically.

    Searches in order:
    1. Explicit path (if provided and exists)
    2. assets/config/default.toml relative to this module / project root
    3. asserts/config/default.toml (for backward compatibility)
    4. Current working directory relative paths
    """
    if explicit_path:
        p = Path(explicit_path).expanduser().resolve()
        if p.is_file():
            return p

    # Find relative to this source file:
    # default.py -> config/ -> googlepy/ -> src/ -> project root
    current_dir = Path(__file__).resolve().parent
    candidates = [
        current_dir.parent.parent.parent / "assets" / "config" / "default.toml",
        current_dir.parent.parent.parent / "asserts" / "config" / "default.toml",
        current_dir.parent.parent / "assets" / "config" / "default.toml",
        current_dir.parent.parent / "asserts" / "config" / "default.toml",
        Path.cwd() / "assets" / "config" / "default.toml",
        Path.cwd() / "asserts" / "config" / "default.toml",
        Path.cwd() / "lib" / "googlepy" / "assets" / "config" / "default.toml",
        Path.cwd() / "lib" / "googlepy" / "asserts" / "config" / "default.toml",
    ]

    for cand in candidates:
        if cand.is_file():
            return cand

    # Default fallback path even if not yet created on disk
    return candidates[0]


def get_default_config(keys: list[str] | None = None, config_path: str | Path | None = None) -> Any:
    """Load and return configuration from TOML default config file.

    :param keys: Optional list of nested keys to navigate (e.g. ["google", "scopes"]).
    :param config_path: Optional explicit path to the TOML configuration file.
    :return: Full dictionary or navigated sub-value.
    """
    path = find_default_config_path(config_path)
    if not path.is_file():
        raise FileNotFoundError(f"Default config file not found at {path}")

    with open(path, "rb") as f:
        data = tomllib.load(f)

    if keys:
        for key in keys:
            if not isinstance(data, dict) or key not in data:
                raise KeyError(f"Key '{key}' not found in default config at {path}")
            data = data[key]

    return data
