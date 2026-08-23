import gspread
import config.env as env
from enum import Enum

class GoogleClientType(Enum):
    SERVICE_ACCOUNT = "SERVICE_ACCOUNT"
    OAUTH2 = "OAUTH2"
    API_KEY = "API_KEY"
    CREDENTIALS = "CREDENTIALS"

def get_client_service_file(service_key_file: str| None) -> gspread.Client:
    """
    Create a gspread client using the provided service key file.

    Args:
        service_key_file (str): Path to the service key JSON file.

    Returns:
        gspread.Client: An authenticated gspread client.
    """
    if not service_key_file:
        service_key_file = env.GOOGLE_SERVICE_KEY_FILE
        if not service_key_file:
            raise ValueError("Service key file path must be provided. or set the GOOGLE_SERVICE_KEY_FILE environment variable.")
    return gspread.service_account(filename=service_key_file)

def get_client(TYPE: GoogleClientType=GoogleClientType.SERVICE_ACCOUNT) -> gspread.Client:
    """
    Create a gspread client using the default service key file.

    Returns:
        gspread.Client: An authenticated gspread client.
    """
    if TYPE == GoogleClientType.SERVICE_ACCOUNT:
        return get_client_service_file()
    else:
        raise ValueError(f"Unsupported client type: {TYPE}")