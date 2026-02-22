from dotenv import load_dotenv
from google.oauth2 import service_account
import gspread
import os

load_dotenv()

get_scopes = lambda: list(os.getenv("GOOGLE_SCOPES", "").split(","))

SERVICE_KEY_FILE = os.getenv("SERVICE_KEY_FILE", "")
SCOPES = get_scopes()


def get_client_service_account(service_key_file: str = SERVICE_KEY_FILE, scopes: list = SCOPES):
    if not SCOPES or len(SCOPES) == 0:
        raise ValueError("GOOGLE_SCOPES environment variable must be set and contain at least one scope.")
    if not service_key_file or not os.path.isfile(service_key_file):
        raise ValueError("SERVICE_KEY_FILE environment variable must be set and point to a valid service account JSON file.")

    credentials = service_account.Credentials.from_service_account_file(
        service_key_file,
        scopes=scopes,
    )
    client = gspread.authorize(credentials)

    # Check connectivity - will raise an exception if auth/network fails
    client.list_spreadsheet_files()
    return client, credentials

