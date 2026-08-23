import gspread

def get_client_service_file(service_key_file: str):
    """
    Create a gspread client using the provided service key file.

    Args:
        service_key_file (str): Path to the service key JSON file.

    Returns:
        gspread.Client: An authenticated gspread client.
    """
    if not service_key_file:
        raise ValueError("Service key file path must be provided.")
    
    return gspread.service_account(filename=service_key_file)