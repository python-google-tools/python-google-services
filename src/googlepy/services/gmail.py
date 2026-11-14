from __future__ import annotations

import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Generator

from googlepy.client.base import GoogleServiceClient
from googlepy.functional.pagination import paginate


def _build_raw_message(
    to: str,
    subject: str,
    body: str,
    html: bool = False,
    cc: str | None = None,
    bcc: str | None = None,
) -> str:
    message = MIMEMultipart("alternative") if html else MIMEText(body)
    message["to"] = to
    message["subject"] = subject

    if cc:
        message["cc"] = cc
    if bcc:
        message["bcc"] = bcc

    if html:
        part_plain = MIMEText(body, "plain")
        part_html = MIMEText(body, "html")
        message.attach(part_plain)
        message.attach(part_html)

    raw_bytes = message.as_bytes()
    return base64.urlsafe_b64encode(raw_bytes).decode("utf-8")


def send_message(
    client: GoogleServiceClient,
    to: str,
    subject: str,
    body: str,
    html: bool = False,
    cc: str | None = None,
    bcc: str | None = None,
    user_id: str = "me",
) -> dict[str, Any]:
    """Send an email message via Gmail API.

    Args:
        client: Authenticated GoogleServiceClient.
        to: Primary recipient email address.
        subject: Email subject line.
        body: Email body text (plain text or HTML).
        html: If True, formats body as multipart/alternative HTML email.
        cc: Optional CC recipients.
        bcc: Optional BCC recipients.
        user_id: Target user mailbox (default 'me').

    Returns:
        Sent message metadata containing 'id' and 'threadId'.
    """
    if not to or not subject:
        raise ValueError("Recipient 'to' and 'subject' are required.")

    raw = _build_raw_message(to=to, subject=subject, body=body, html=html, cc=cc, bcc=bcc)
    return client.post(f"users/{user_id}/messages/send", json={"raw": raw})


def create_draft(
    client: GoogleServiceClient,
    to: str,
    subject: str,
    body: str,
    html: bool = False,
    user_id: str = "me",
) -> dict[str, Any]:
    """Create an email draft in Gmail.

    Args:
        client: Authenticated GoogleServiceClient.
        to: Recipient email address.
        subject: Draft subject line.
        body: Draft body text.
        html: Whether the content is HTML.
        user_id: Target mailbox (default 'me').

    Returns:
        Created draft metadata.
    """
    if not to or not subject:
        raise ValueError("Recipient 'to' and 'subject' are required.")

    raw = _build_raw_message(to=to, subject=subject, body=body, html=html)
    return client.post(f"users/{user_id}/drafts", json={"message": {"raw": raw}})


def list_messages(
    client: GoogleServiceClient,
    query: str | None = None,
    max_results: int = 100,
    user_id: str = "me",
) -> list[dict[str, Any]]:
    """List messages matching an optional Gmail search query.

    Args:
        client: Authenticated GoogleServiceClient.
        query: Gmail query filter string (e.g. 'is:unread from:boss@company.com').
        max_results: Maximum number of messages to return.
        user_id: Mailbox identifier.

    Returns:
        List of message summaries containing 'id' and 'threadId'.
    """
    params: dict[str, Any] = {"maxResults": max_results}
    if query:
        params["q"] = query

    res = client.get(f"users/{user_id}/messages", params=params)
    return res.get("messages", []) if isinstance(res, dict) else []


def iter_messages(
    client: GoogleServiceClient,
    query: str | None = None,
    page_size: int = 100,
    max_items: int | None = None,
    user_id: str = "me",
) -> Generator[dict[str, Any], None, None]:
    """Lazily generate messages across pages without loading all into memory.

    Args:
        client: Authenticated GoogleServiceClient.
        query: Gmail query filter string.
        page_size: Page size per request.
        max_items: Optional maximum total items to yield.
        user_id: Mailbox identifier.

    Yields:
        Individual message summary dictionaries.
    """
    params: dict[str, Any] = {"maxResults": page_size}
    if query:
        params["q"] = query

    yield from paginate(
        fetch_page=lambda **kw: client.get(f"users/{user_id}/messages", params=kw.get("params", kw)),
        items_key="messages",
        page_token_param="pageToken",
        next_token_key="nextPageToken",
        max_items=max_items,
        params=params,
    )


def get_message(
    client: GoogleServiceClient,
    message_id: str,
    user_id: str = "me",
    format: str = "full",
) -> dict[str, Any]:
    """Retrieve details for a specific email message.

    Args:
        client: Authenticated GoogleServiceClient.
        message_id: Unique message ID.
        user_id: Mailbox identifier.
        format: Representation format ('full', 'metadata', 'minimal', 'raw').

    Returns:
        Full message resource dictionary.
    """
    if not message_id:
        raise ValueError("message_id is required.")
    return client.get(f"users/{user_id}/messages/{message_id}", params={"format": format})


def list_labels(client: GoogleServiceClient, user_id: str = "me") -> list[dict[str, Any]]:
    """List all Gmail labels in the user's mailbox."""
    res = client.get(f"users/{user_id}/labels")
    return res.get("labels", []) if isinstance(res, dict) else []
