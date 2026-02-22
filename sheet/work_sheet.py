
def list_worksheets(sheet):
        """List all sheets in the worksheet."""
        if not sheet:
            raise ValueError("Sheet object is required.")
        return sheet.worksheets()
def worksheet_contains(sheet, name):
        """Check if a sheet with the given name exists in the worksheet."""
        if not sheet:
            raise ValueError("Sheet object is required.")
        if not name:
            raise ValueError("Sheet name is required.")
        return any(ws.title == name for ws in sheet.worksheets())
def count_worksheet(sheet):
        """Get the number of sheets in the worksheet."""
        if not sheet:
            raise ValueError("Sheet object is required.")
        return len(sheet.worksheets())

def info_worksheet(sheet, name):
        """Get information about a specific sheet by name."""
        if not sheet:
            raise ValueError("Sheet object is required.")
        if not name:
            raise ValueError("Sheet name is required.")
        for ws in sheet.worksheets():
            if ws.title == name:
                return {
                    "title": ws.title,
                    "index": ws.index,
                    "row_count": ws.row_count,
                    "col_count": ws.col_count,
                    "total_cells": ws.row_count * ws.col_count,
                    "color": ws.color,

                }
        raise ValueError(f"Sheet with name '{name}' not found.")

def set_worksheet_title(sheet, old_name, new_name):
        """Set the title of a sheet."""
        if not sheet:
            raise ValueError("Sheet object is required.")
        if not old_name or not new_name:
            raise ValueError("Both old and new sheet names are required.")
        for ws in sheet.worksheets():
            if ws.title == old_name:
                ws.update_title(new_name)
                return
        raise ValueError(f"Sheet with name '{old_name}' not found.")

def delete_worksheet(sheet, name):
        """Delete a sheet by name."""
        if not sheet:
            raise ValueError("Sheet object is required.")
        if not name:
            raise ValueError("Sheet name is required.")
        for ws in sheet.worksheets():
            if ws.title == name:
                sheet.del_worksheet(ws)
                return
        raise ValueError(f"Sheet with name '{name}' not found.")

def add_worksheet(sheet, name, rows=100, cols=26):
        """Add a new sheet to the worksheet."""
        if not sheet:
            raise ValueError("Sheet object is required.")
        if not name:
            raise ValueError("Sheet name is required.")
        if worksheet_contains(sheet, name):
            raise ValueError(f"Sheet with name '{name}' already exists.")
        sheet.add_worksheet(title=name, rows=rows, cols=cols)
def clear_worksheet(sheet, name):
        """Clear all data from a sheet by name."""
        if not sheet:
            raise ValueError("Sheet object is required.")
        if not name:
            raise ValueError("Sheet name is required.")
        for ws in sheet.worksheets():
            if ws.title == name:
                ws.clear()
                return
        raise ValueError(f"Sheet with name '{name}' not found.")
def copy_worksheet(sheet, source_name, target_name):
        """Copy a sheet within the same worksheet."""
        if not sheet:
            raise ValueError("Sheet object is required.")
        if not source_name or not target_name:
            raise ValueError("Both source and target sheet names are required.")
        source_ws = None
        for ws in sheet.worksheets():
            if ws.title == source_name:
                source_ws = ws
                break
        if not source_ws:
            raise ValueError(f"Source sheet with name '{source_name}' not found.")
        if worksheet_contains(sheet, target_name):
            raise ValueError(f"Target sheet with name '{target_name}' already exists.")
        new_ws = sheet.add_worksheet(title=target_name, rows=source_ws.row_count, cols=source_ws.col_count)
        new_ws.update_cells(source_ws.get_all_cells())
def set_worksheet_color(sheet, name, color):
        """Set the background color of a sheet."""
        if not sheet:
            raise ValueError("Sheet object is required.")
        if not name:
            raise ValueError("Sheet name is required.")
        if not color or not isinstance(color, dict):
            raise ValueError("Color must be a dictionary with 'red', 'green', and 'blue' keys.")
        for ws in sheet.worksheets():
            if ws.title == name:
                ws.update_color(color)
                return
        raise ValueError(f"Sheet with name '{name}' not found.")