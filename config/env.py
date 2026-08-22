import os

from dotenv import load_dotenv


load_dotenv()

google_SCOPES = os.getenv("GOOGLE_SCOPES", "",).split(",")