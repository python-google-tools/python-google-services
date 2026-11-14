from __future__ import annotations

from typing import Any, Generator
from googlepy.client.base import GoogleServiceClient
from googlepy.functional.pagination import paginate


def list_files(
    client: GoogleServiceClient,
    query: str | None = None,
    page_size: int = 100,
    fields: str = "files(id, name, mimeType, modifiedTime, size)",
) -> list[dict[str, Any]]:
    """List files in Google Drive matching an optional search query.

    Args:
        client: Authenticated GoogleServiceClient.
        query: Drive query filter string (e.g. "name contains 'report' and trashed = false").
        page_size: Number of files to return per page.
        fields: Partial fields projection string.

    Returns:
        List of file metadata dictionaries.
    """
    params: dict[str, Any] = {"pageSize": page_size, "fields": fields}
    if query:
        params["q"] = query

    res = client.get("files", params=params)
    return res.get("files", []) if isinstance(res, dict) else []


def iter_files(
    client: GoogleServiceClient,
    query: str | None = None,
    page_size: int = 100,
    fields: str = "nextPageToken, files(id, name, mimeType, modifiedTime, size)",
    max_items: int | None = None,
) -> Generator[dict[str, Any], None, None]:
    """Lazily generate files across multiple Drive pages without loading all into memory.

    Args:
        client: Authenticated GoogleServiceClient.
        query: Drive query filter string.
        page_size: Page size per HTTP request.
        fields: Projection fields (must include nextPageToken).
        max_items: Optional maximum number of total items to yield.

    Yields:
        Individual file metadata dictionaries.
    """
    params: dict[str, Any] = {"pageSize": page_size, "fields": fields}
    if query:
        params["q"] = query

    yield from paginate(
        fetch_page=lambda **kw: client.get("files", params=kw.get("params", kw)),
        items_key="files",
        page_token_param="pageToken",
        next_token_key="nextPageToken",
        max_items=max_items,
        params=params,
    )


def find_file_by_name(
    client: GoogleServiceClient,
    name: str,
    parent_id: str | None = None,
) -> dict[str, Any] | None:
    """Find a single active file or folder by exact name.

    Args:
        client: Authenticated GoogleServiceClient.
        name: Target file or folder name.
        parent_id: Optional parent folder ID to restrict the search.

    Returns:
        Dictionary of file metadata, or None if not found.
    """
    if not name:
        raise ValueError("File name must be specified.")

    query = f"name = '{name}' and trashed = false"
    if parent_id:
        query += f" and '{parent_id}' in parents"

    files = list_files(client, query=query, page_size=1)
    return files[0] if files else None


def create_folder(
    client: GoogleServiceClient,
    folder_name: str,
    parent_id: str | None = None,
) -> dict[str, Any]:
    """Create a new folder in Google Drive.

    Args:
        client: Authenticated GoogleServiceClient.
        folder_name: Name of the folder to create.
        parent_id: Optional parent folder ID.

    Returns:
        Created folder metadata dictionary containing 'id' and 'name'.
    """
    if not folder_name:
        raise ValueError("Folder name must be specified.")

    metadata: dict[str, Any] = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if parent_id:
        metadata["parents"] = [parent_id]

    return client.post("files", json=metadata)


def upload_file(
    client: GoogleServiceClient,
    name: str,
    content: str | bytes,
    mime_type: str = "application/octet-stream",
    parent_id: str | None = None,
) -> dict[str, Any]:
    """Upload or create a file with content in Google Drive.

    Args:
        client: Authenticated GoogleServiceClient.
        name: Name of the file.
        content: String or bytes data to store in the file.
        mime_type: MIME type of the content.
        parent_id: Optional parent folder ID.

    Returns:
        Created file metadata dictionary.
    """
    if not name:
        raise ValueError("File name must be specified.")

    metadata: dict[str, Any] = {"name": name, "mimeType": mime_type}
    if parent_id:
        metadata["parents"] = [parent_id]

    file_obj = client.post("files", json=metadata)
    file_id = file_obj.get("id")

    if file_id and content:
        upload_url = f"https://www.googleapis.com/upload/drive/v3/files/{file_id}?uploadType=media"
        body = content.encode("utf-8") if isinstance(content, str) else content
        client.patch(upload_url, data=body, headers={"Content-Type": mime_type})

    return file_obj


def download_file(client: GoogleServiceClient, file_id: str) -> bytes:
    """Download the binary or text content of a file by its ID.

    Args:
        client: Authenticated GoogleServiceClient.
        file_id: The ID of the file to download.

    Returns:
        Bytes containing the file payload.
    """
    if not file_id:
        raise ValueError("file_id is required.")
    resp = client.request("GET", f"files/{file_id}?alt=media")
    return resp.content


def delete_file(client: GoogleServiceClient, file_id: str) -> None:
    """Permanently delete a file or folder from Google Drive.

    Args:
        client: Authenticated GoogleServiceClient.
        file_id: ID of the file to delete.
    """
    if not file_id:
        raise ValueError("file_id is required.")
    client.delete(f"files/{file_id}")


def share_file(
    client: GoogleServiceClient,
    file_id: str,
    email: str | None = None,
    role: str = "reader",
    type: str = "user",
) -> dict[str, Any]:
    """Share a file by adding permissions.

    Args:
        client: Authenticated GoogleServiceClient.
        file_id: The ID of the file to share.
        email: Email address of the user or group to grant access to.
        role: Permission role ('reader', 'commenter', 'writer', 'owner').
        type: Permission type ('user', 'group', 'domain', 'anyone').

    Returns:
        Created permission metadata.
    """
    if not file_id:
        raise ValueError("file_id is required.")

    body: dict[str, Any] = {"role": role, "type": type}
    if email:
        body["emailAddress"] = email

    return client.post(f"files/{file_id}/permissions", json=body)
