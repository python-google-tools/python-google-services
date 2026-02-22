from ..auth import get_client


def _get_sheet_by_id(client, spreadsheet_id):
    try:
        spreadsheet = client.open_by_key(spreadsheet_id)
        return spreadsheet
    except Exception as e:
        raise ValueError(f"Error accessing spreadsheet: {e}")


def _get_sheet_by_name(client, spreadsheet_name):
    try:
        spreadsheet = client.open(spreadsheet_name)
        return spreadsheet
    except Exception as e:
        raise ValueError(f"Error accessing spreadsheet: {e}")


def _get_sheet_by_url(client, spreadsheet_url):
    try:
        spreadsheet = client.open_by_url(spreadsheet_url)
        return spreadsheet
    except Exception as e:
        raise ValueError(f"Error accessing spreadsheet: {e}")


def _get_sheet_by_email(client, email):
    try:
        spreadsheet = client.open_by_email(email)
        return spreadsheet
    except Exception as e:
        raise ValueError(f"Error accessing spreadsheet: {e}")


def get_sheet(client, *, id=None, name=None, url=None, email=None):
    sheet = None
    if sum(x is not None for x in [id, name, url, email]) != 1:
        raise ValueError(
            "Must provide exactly one of id, name, url, or email to identify the spreadsheet."
        )
    if id:
        return _get_sheet_by_id(client, id)
    elif name:
        return _get_sheet_by_name(client, name)
    elif url:
        return _get_sheet_by_url(client, url)
    elif email:
        return _get_sheet_by_email(client, email)


sheet = get_sheet(get_client(), name="Test Sheet")
print(sheet.sheet1.row_values(1))
