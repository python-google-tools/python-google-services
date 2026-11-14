"""Google Sheets access helpers."""

from __future__ import annotations

import gspread
from googlepy.client.base import GoogleClientType
from googlepy.client.sheet import get_client
from googlepy.services.sheets import (
    append_rows,
    clear_worksheet,
    create_worksheet,
    delete_worksheet,
    get_all_records,
    get_spreadsheet,
    get_worksheet,
    list_worksheets,
    read_range,
    worksheet_exists,
    write_range,
)


def get_google_sheet_by_id(
    sheet_client_Type: GoogleClientType | str,
    sheet_id: str,
) -> gspread.Spreadsheet:
    """Fetch a Google Sheet by ID."""
    if not sheet_id:
        raise ValueError("Sheet ID must be provided.")

    if isinstance(sheet_client_Type, str):
        sheet_client_Type = GoogleClientType(sheet_client_Type)

    client = get_client(sheet_client_Type)
    return client.open_by_key(sheet_id)


__all__ = [
    "GoogleClientType",
    "get_google_sheet_by_id",
    "get_spreadsheet",
    "list_worksheets",
    "worksheet_exists",
    "get_worksheet",
    "create_worksheet",
    "delete_worksheet",
    "read_range",
    "write_range",
    "append_rows",
    "clear_worksheet",
    "get_all_records",
]
