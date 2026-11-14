from __future__ import annotations

from typing import Any, Generator
from googlepy.client.base import GoogleServiceClient
from googlepy.functional.pagination import paginate


def list_events(
    client: GoogleServiceClient,
    calendar_id: str = "primary",
    time_min: str | None = None,
    max_results: int = 250,
    single_events: bool = True,
    order_by: str = "startTime",
) -> list[dict[str, Any]]:
    """List events from the specified calendar.

    Args:
        client: Authenticated GoogleServiceClient.
        calendar_id: Calendar identifier (default 'primary').
        time_min: Lower bound for an event's end time to filter by (ISO 8601).
        max_results: Maximum events to return.
        single_events: Whether to expand recurring events into instances.
        order_by: Ordering parameter ('startTime' or 'updated').

    Returns:
        List of event resource dictionaries.
    """
    params: dict[str, Any] = {
        "maxResults": max_results,
        "singleEvents": single_events,
        "orderBy": order_by,
    }
    if time_min:
        params["timeMin"] = time_min

    res = client.get(f"calendars/{calendar_id}/events", params=params)
    return res.get("items", []) if isinstance(res, dict) else []


def iter_events(
    client: GoogleServiceClient,
    calendar_id: str = "primary",
    time_min: str | None = None,
    page_size: int = 250,
    single_events: bool = True,
    order_by: str = "startTime",
    max_items: int | None = None,
) -> Generator[dict[str, Any], None, None]:
    """Lazily generate calendar events across pages.

    Args:
        client: Authenticated GoogleServiceClient.
        calendar_id: Calendar identifier.
        time_min: Minimum start timestamp.
        page_size: Events per request page.
        single_events: Expand recurring events.
        order_by: Sort order.
        max_items: Optional maximum total events to yield.

    Yields:
        Individual event dictionaries.
    """
    params: dict[str, Any] = {
        "maxResults": page_size,
        "singleEvents": single_events,
        "orderBy": order_by,
    }
    if time_min:
        params["timeMin"] = time_min

    yield from paginate(
        fetch_page=lambda **kw: client.get(f"calendars/{calendar_id}/events", params=kw.get("params", kw)),
        items_key="items",
        page_token_param="pageToken",
        next_token_key="nextPageToken",
        max_items=max_items,
        params=params,
    )


def create_event(
    client: GoogleServiceClient,
    summary: str,
    start_time: str,
    end_time: str,
    description: str | None = None,
    location: str | None = None,
    calendar_id: str = "primary",
    time_zone: str = "UTC",
) -> dict[str, Any]:
    """Create a new event in Google Calendar.

    Args:
        client: Authenticated GoogleServiceClient.
        summary: Event title.
        start_time: Start date/time ISO string (e.g. '2026-11-15T10:00:00Z').
        end_time: End date/time ISO string.
        description: Description/agenda.
        location: Event location.
        calendar_id: Target calendar.
        time_zone: Time zone identifier.

    Returns:
        Created event resource.
    """
    if not summary:
        raise ValueError("Event summary is required.")
    if not start_time or not end_time:
        raise ValueError("Both start_time and end_time are required.")

    start_key = "date" if "T" not in start_time else "dateTime"
    end_key = "date" if "T" not in end_time else "dateTime"

    event: dict[str, Any] = {
        "summary": summary,
        "start": {start_key: start_time, "timeZone": time_zone},
        "end": {end_key: end_time, "timeZone": time_zone},
    }
    if description:
        event["description"] = description
    if location:
        event["location"] = location

    return client.post(f"calendars/{calendar_id}/events", json=event)


def get_event(
    client: GoogleServiceClient,
    event_id: str,
    calendar_id: str = "primary",
) -> dict[str, Any]:
    """Retrieve details for a specific event."""
    if not event_id:
        raise ValueError("event_id is required.")
    return client.get(f"calendars/{calendar_id}/events/{event_id}")


def delete_event(
    client: GoogleServiceClient,
    event_id: str,
    calendar_id: str = "primary",
) -> None:
    """Delete an event from Google Calendar."""
    if not event_id:
        raise ValueError("event_id is required.")
    client.delete(f"calendars/{calendar_id}/events/{event_id}")


def list_calendars(client: GoogleServiceClient) -> list[dict[str, Any]]:
    """List all Google Calendars accessible by the user."""
    res = client.get("users/me/calendarList")
    return res.get("items", []) if isinstance(res, dict) else []
