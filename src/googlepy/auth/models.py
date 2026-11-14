from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from pydantic import BaseModel, field_validator


class ApiKeyAuth(BaseModel):
    """Validation model for API-key authentication."""

    api_key: str

    @field_validator("api_key")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("api_key must be a non-empty string")
        return value


class ServiceAccountAuth(BaseModel):
    """Validation model for service account key authentication."""

    key_file: str | None = None
    key_info: dict[str, Any] | None = None

    @field_validator("key_file")
    @classmethod
    def _validate_file_path(cls, value: str | None) -> str | None:
        if value is not None:
            value = value.strip()
            if not value:
                raise ValueError("key_file cannot be empty")
        return value


class OAuthAuth(BaseModel):
    """Validation model for OAuth authentication paths."""

    client_secret_file: str
    token_file: str = "token.json"

    @field_validator("client_secret_file")
    @classmethod
    def _validate_secret_path(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("client_secret_file must be a non-empty string")
        return value
