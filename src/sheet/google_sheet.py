from client import sheet as sheet_client
def get_google_sheet_by_id(sheet_client_Type: sheet_client.GoogleClientType, sheet_id: str):
    # Implementation for fetching Google Sheet by ID
    if not sheet_id:
        raise ValueError("Sheet ID must be provided.")
    return sheet_client.get_client(sheet_client_Type).open_by_key(sheet_id)