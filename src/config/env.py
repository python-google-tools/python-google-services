from dotenv import load_dotenv
import os
import config
load_dotenv()

# Google API scopes for accessing Google Sheets and Drive
 GOOGLE_SCOPES = os.getenv("GOOGLE_SCOPES",config.get_default_config(["oauth","scopes"]))
# Path to the service key file for Google API authentication
GOOGLE_SERVICE_KEY_FILE = os.getenv("SERVICE_KEY_FILE")
# Google API key for accessing Google services
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# Google client ID for OAuth 2.0 authentication
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
# Google client secret for OAuth 2.0 authentication
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
# Google URL for accessing Google Sheets API
GOOGLE_URL = os.getenv("GOOGLE_URL")
# Google Sheet ID for identifying the specific Google Sheet to work with
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
# Google Sheet name for identifying the specific sheet within the Google Sheet to work with
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")