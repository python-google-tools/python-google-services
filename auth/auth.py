from dotenv import load_dotenv
import os

load_dotenv()

get_scopes = lambda: list(os.getenv("GOOGLE_SCOPES", "").split(","))

