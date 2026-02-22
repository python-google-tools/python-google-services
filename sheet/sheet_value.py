import gspread


def sheet_rows(worksheet, name):
    """Get the number of rows in a sheet by name."""
    if not worksheet:
        raise ValueError("Sheet object is required.")
    if not name:
        raise ValueError("Sheet name is required.")
    return worksheet.row_count


def sheet_cols(worksheet, name):
    """Get the number of columns in a sheet by name."""
    if not worksheet:
        raise ValueError("Sheet object is required.")
    if not name:
        raise ValueError("Sheet name is required.")
    return worksheet.col_count


def sheet_values(worksheet, name):
    """Get all values from a sheet by name."""
    if not worksheet:
        raise ValueError("Sheet object is required.")
    if not name:
        raise ValueError("Sheet name is required.")
    return worksheet.get_all_values()


def construct_cell_range(start_row, start_col, end_row, end_col):
    """Construct a cell range string from start and end row/column indices."""
    if not all(
        isinstance(x, int) and x > 0 for x in [start_row, start_col, end_row, end_col]
    ):
        raise ValueError("Row and column indices must be positive integers.")
    start_cell = gspread.utils.rowcol_to_a1(start_row, start_col)
    end_cell = gspread.utils.rowcol_to_a1(end_row, end_col)
    return f"{start_cell}:{end_cell}"


def values_by_range(worksheet, cell_range):
    """Get values from a specific range in a sheet by name."""
    if not worksheet:
        raise ValueError("Sheet object is required.")
    if not cell_range:
        raise ValueError("Cell range is required.")
    return worksheet.get(cell_range)
