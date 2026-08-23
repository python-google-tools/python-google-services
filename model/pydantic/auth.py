"""Pydantic validation models for authentication inputs."""

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
