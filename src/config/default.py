"""Compatibility module: forwards to googlepy.config.default."""

from googlepy.config.default import find_default_config_path, get_default_config

__all__ = ["find_default_config_path", "get_default_config"]
