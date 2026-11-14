from __future__ import annotations

from typing import Any
from googlepy.client.base import GoogleServiceClient


def create_document(client: GoogleServiceClient, title: str) -> dict[str, Any]:
    """Create a new Google Doc with the specified title."""
    if not title:
        raise ValueError("Document title is required.")
    return client.post("documents", json={"title": title})


def get_document(client: GoogleServiceClient, document_id: str) -> dict[str, Any]:
    """Retrieve full metadata and content structure for a Google Doc."""
    if not document_id:
        raise ValueError("document_id is required.")
    return client.get(f"documents/{document_id}")


def get_document_text(client: GoogleServiceClient, document_id: str) -> str:
    """Extract and concatenate all plain text from a Google Doc body."""
    doc = get_document(client, document_id)
    content = doc.get("body", {}).get("content", [])
    extracted: list[str] = []

    for element in content:
        paragraph = element.get("paragraph")
        if not paragraph:
            continue
        for elem in paragraph.get("elements", []):
            text_run = elem.get("textRun")
            if text_run and "content" in text_run:
                extracted.append(text_run["content"])

    return "".join(extracted)


def batch_update_document(
    client: GoogleServiceClient,
    document_id: str,
    requests: list[dict[str, Any]],
) -> dict[str, Any]:
    """Execute a batchUpdate command on a Google Doc."""
    if not document_id:
        raise ValueError("document_id is required.")
    return client.post(f"documents/{document_id}:batchUpdate", json={"requests": requests})


def insert_text(
    client: GoogleServiceClient,
    document_id: str,
    text: str,
    index: int = 1,
) -> dict[str, Any]:
    """Insert text into a Google Doc at the specified index."""
    if not text:
        return {}
    request = {
        "insertText": {
            "location": {"index": index},
            "text": text,
        }
    }
    return batch_update_document(client, document_id, [request])


def replace_all_text(
    client: GoogleServiceClient,
    document_id: str,
    target_text: str,
    replacement_text: str,
    match_case: bool = True,
) -> dict[str, Any]:
    """Find and replace all occurrences of a string in a Google Doc."""
    if not target_text:
        raise ValueError("target_text must be non-empty.")

    request = {
        "replaceAllText": {
            "containsText": {
                "text": target_text,
                "matchCase": match_case,
            },
            "replaceText": replacement_text,
        }
    }
    return batch_update_document(client, document_id, [request])
