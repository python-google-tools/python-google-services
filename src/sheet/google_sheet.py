
def get_google_sheet_by_id(client,sheet_id: str):
    # Implementation for fetching Google Sheet by ID
    return client.open_by_key(sheet_id)