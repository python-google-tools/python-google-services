"""Lazy generator for Google API paginated endpoints.

Yields items one by one across pages without loading all results into memory.
"""

from __future__ import annotations

from typing import Any, Callable, Generator, Mapping


def paginate(
    fetch_page: Callable[..., Mapping[str, Any]],
    items_key: str = "items",
    page_token_param: str = "pageToken",
    next_token_key: str = "nextPageToken",
    max_items: int | None = None,
    **kwargs: Any,
) -> Generator[Any, None, None]:
    """Lazily generate items from a paginated Google REST API endpoint.

    Args:
        fetch_page: Function that accepts kwargs and returns a dictionary response.
        items_key: Key in the response dictionary containing the list of items.
        page_token_param: Query parameter name passed to fetch_page for next page.
        next_token_key: Key in the response dictionary containing the next page token.
        max_items: Optional maximum number of total items to yield.
        **kwargs: Initial parameters passed to fetch_page.

    Yields:
        Individual item dictionaries or objects.

    Example:
        >>> for file in paginate(lambda **kw: client.get("files", params=kw), items_key="files"):
        ...     print(file["name"])
    """
    if max_items is not None and max_items <= 0:
        return

    count = 0
    params = dict(kwargs.get("params", {})) if "params" in kwargs else dict(kwargs)
    next_token: str | None = None

    while True:
        current_params = dict(params)
        if next_token:
            current_params[page_token_param] = next_token

        # Call page fetcher
        if "params" in kwargs:
            call_kwargs = dict(kwargs)
            call_kwargs["params"] = current_params
            response = fetch_page(**call_kwargs)
        else:
            response = fetch_page(**current_params)

        if not isinstance(response, Mapping):
            break

        items = response.get(items_key, [])
        if not items:
            break

        for item in items:
            if max_items is not None and count >= max_items:
                return
            yield item
            count += 1
            if max_items is not None and count >= max_items:
                return

        next_token = response.get(next_token_key)
        if not next_token:
            break
