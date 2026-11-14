from __future__ import annotations

from enum import Enum
from typing import Any, Mapping

import requests
from google.auth.credentials import Credentials
from google.auth.transport.requests import AuthorizedSession

from googlepy.exceptions import GoogleAPIError
from googlepy.functional.decorators import retry_with_backoff


class GoogleClientType(str, Enum):
    """Supported Google authentication client types."""

    SERVICE_ACCOUNT = "SERVICE_ACCOUNT"
    OAUTH2 = "OAUTH2"
    API_KEY = "API_KEY"
    CREDENTIALS = "CREDENTIALS"


class GoogleServiceClient:
    """Standardized, stateless HTTP client for Google REST APIs using an AuthorizedSession.

    Handles bearer token authorization, token auto-refresh, base URL prefixing,
    exponential backoff on transient errors (429/500/503), and structured error translation.
    """

    def __init__(
        self,
        credentials: Credentials | None = None,
        base_url: str = "",
        session: requests.Session | None = None,
        api_key: str | None = None,
        max_retries: int = 3,
    ):
        """Initialize a GoogleServiceClient.

        Args:
            credentials: Pre-built google.auth Credentials instance.
            base_url: Base URL prefix (e.g. 'https://www.googleapis.com/drive/v3').
            session: Injectable requests.Session (useful for testing and mocking).
            api_key: Optional API key for simple query parameter authentication.
            max_retries: Maximum number of retries for transient errors (429, 500, 503).
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.max_retries = max_retries

        if session is not None:
            self.session = session
        elif credentials is not None:
            self.session = AuthorizedSession(credentials)
        else:
            self.session = requests.Session()

    def _build_url(self, endpoint: str) -> str:
        """Construct full URL from base_url and endpoint path."""
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return endpoint
        endpoint = endpoint.lstrip("/")
        if self.base_url:
            return f"{self.base_url}/{endpoint}"
        return f"/{endpoint}"

    def request(
        self,
        method: str,
        endpoint: str,
        params: Mapping[str, Any] | None = None,
        json: Any = None,
        data: Any = None,
        headers: Mapping[str, str] | None = None,
        timeout: float = 30.0,
        retry: bool = True,
    ) -> requests.Response:
        """Execute an authorized HTTP request with optional retry on transient errors.

        Args:
            method: HTTP verb ('GET', 'POST', 'PUT', 'PATCH', 'DELETE').
            endpoint: Relative endpoint path or absolute URL.
            params: URL query parameters dictionary.
            json: JSON-serializable request payload.
            data: Raw request body data.
            headers: Custom request headers.
            timeout: Request timeout in seconds.
            retry: Whether to retry on transient HTTP 429/500/503 errors.

        Returns:
            requests.Response object.

        Raises:
            GoogleAPIError: If the server returns a 4xx or 5xx status code.
        """
        url = self._build_url(endpoint)
        query_params = dict(params or {})
        if self.api_key and "key" not in query_params:
            query_params["key"] = self.api_key

        req_headers = dict(headers or {})

        def _execute_http() -> requests.Response:
            response = self.session.request(
                method=method,
                url=url,
                params=query_params if query_params else None,
                json=json,
                data=data,
                headers=req_headers if req_headers else None,
                timeout=timeout,
            )

            if not response.ok:
                error_msg = response.text
                details = None
                try:
                    err_json = response.json()
                    if "error" in err_json:
                        err_obj = err_json["error"]
                        error_msg = err_obj.get("message", response.text)
                        details = err_obj
                except Exception:
                    pass
                raise GoogleAPIError(response.status_code, error_msg, details)

            return response

        if retry and self.max_retries > 0:
            retry_runner = retry_with_backoff(max_retries=self.max_retries)(_execute_http)
            return retry_runner()

        return _execute_http()

    def get(self, endpoint: str, params: Mapping[str, Any] | None = None, **kwargs: Any) -> Any:
        """Send a GET request and parse JSON response."""
        resp = self.request("GET", endpoint, params=params, **kwargs)
        if resp.content:
            try:
                return resp.json()
            except Exception:
                return resp.content
        return None

    def post(
        self,
        endpoint: str,
        json: Any = None,
        data: Any = None,
        params: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Send a POST request and parse JSON response."""
        resp = self.request("POST", endpoint, params=params, json=json, data=data, **kwargs)
        if resp.content:
            try:
                return resp.json()
            except Exception:
                return resp.content
        return None

    def put(
        self,
        endpoint: str,
        json: Any = None,
        data: Any = None,
        params: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Send a PUT request and parse JSON response."""
        resp = self.request("PUT", endpoint, params=params, json=json, data=data, **kwargs)
        if resp.content:
            try:
                return resp.json()
            except Exception:
                return resp.content
        return None

    def patch(
        self,
        endpoint: str,
        json: Any = None,
        data: Any = None,
        params: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Send a PATCH request and parse JSON response."""
        resp = self.request("PATCH", endpoint, params=params, json=json, data=data, **kwargs)
        if resp.content:
            try:
                return resp.json()
            except Exception:
                return resp.content
        return None

    def delete(self, endpoint: str, params: Mapping[str, Any] | None = None, **kwargs: Any) -> Any:
        """Send a DELETE request and parse JSON response."""
        resp = self.request("DELETE", endpoint, params=params, **kwargs)
        if resp.content:
            try:
                return resp.json()
            except Exception:
                return resp.content
        return None
