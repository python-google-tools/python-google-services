from __future__ import annotations

from typing import Any
import gspread


def get_spreadsheet(
    client: gspread.Client,
    *,
    id: str | None = None,
    name: str | None = None,
    url: str | None = None,
) -> gspread.Spreadsheet:
    """Open a Google Spreadsheet by exactly one of ID, name, or URL.

    :param client: Authenticated gspread client.
    :param id: Google Spreadsheet ID (key).
    :param name: Name / Title of the spreadsheet.
    :param url: Full URL to the spreadsheet.
    :return: gspread.Spreadsheet object.
    """
    supplied = [x for x in (id, name, url) if x is not None]
    if len(supplied) != 1:
        raise ValueError("Must provide exactly one of 'id', 'name', or 'url' to open a spreadsheet.")

    if id:
        return client.open_by_key(id)
    elif name:
        return client.open(name)
    else:
        assert url is not None
        return client.open_by_url(url)


def list_worksheets(spreadsheet: gspread.Spreadsheet) -> list[gspread.Worksheet]:
    """List all worksheets in a spreadsheet."""
    if not spreadsheet:
        raise ValueError("Spreadsheet object is required.")
    return spreadsheet.worksheets()


def worksheet_exists(spreadsheet: gspread.Spreadsheet, title: str) -> bool:
    """Check if a worksheet with the given title exists."""
    if not spreadsheet or not title:
        return False
    return any(ws.title == title for ws in spreadsheet.worksheets())


def get_worksheet(
    spreadsheet: gspread.Spreadsheet,
    title_or_index: str | int = 0,
) -> gspread.Worksheet:
    """Get a worksheet by title or zero-based index."""
    if not spreadsheet:
        raise ValueError("Spreadsheet object is required.")

    if isinstance(title_or_index, int):
        worksheets = spreadsheet.worksheets()
        if 0 <= title_or_index < len(worksheets):
            return worksheets[title_or_index]
        raise IndexError(f"Worksheet index {title_or_index} out of range (total {len(worksheets)}).")

    try:
        return spreadsheet.worksheet(title_or_index)
    except Exception as e:
        raise ValueError(f"Worksheet with title '{title_or_index}' not found: {e}")


def create_worksheet(
    spreadsheet: gspread.Spreadsheet,
    title: str,
    rows: int = 100,
    cols: int = 26,
) -> gspread.Worksheet:
    """Create a new worksheet in the spreadsheet."""
    if not spreadsheet:
        raise ValueError("Spreadsheet object is required.")
    if not title:
        raise ValueError("Worksheet title is required.")
    if worksheet_exists(spreadsheet, title):
        raise ValueError(f"Worksheet '{title}' already exists.")
    return spreadsheet.add_worksheet(title=title, rows=rows, cols=cols)


def delete_worksheet(spreadsheet: gspread.Spreadsheet, title: str) -> None:
    """Delete a worksheet by title."""
    if not spreadsheet or not title:
        raise ValueError("Spreadsheet and title are required.")
    ws = get_worksheet(spreadsheet, title)
    spreadsheet.del_worksheet(ws)


def read_range(
    worksheet: gspread.Worksheet,
    cell_range: str | None = None,
) -> list[list[Any]]:
    """Read values from a worksheet, optionally bounded by an A1 notation cell range."""
    if not worksheet:
        raise ValueError("Worksheet object is required.")
    if cell_range:
        return worksheet.get(cell_range)
    return worksheet.get_all_values()


def write_range(
    worksheet: gspread.Worksheet,
    cell_range: str,
    values: list[list[Any]],
) -> Any:
    """Write values into a worksheet at the specified A1 notation cell range."""
    if not worksheet or not cell_range:
        raise ValueError("Worksheet and cell_range are required.")
    return worksheet.update(cell_range, values)


def append_rows(
    worksheet: gspread.Worksheet,
    values: list[list[Any]],
) -> Any:
    """Append one or more rows to the end of the worksheet."""
    if not worksheet or not values:
        raise ValueError("Worksheet and values are required.")
    return worksheet.append_rows(values)


def clear_worksheet(worksheet: gspread.Worksheet) -> None:
    """Clear all cells from the worksheet."""
    if not worksheet:
        raise ValueError("Worksheet object is required.")
    worksheet.clear()


def get_all_records(worksheet: gspread.Worksheet) -> list[dict[str, Any]]:
    """Return all records as a list of dictionaries using the first row as headers."""
    if not worksheet:
        raise ValueError("Worksheet object is required.")
    return worksheet.get_all_records()
