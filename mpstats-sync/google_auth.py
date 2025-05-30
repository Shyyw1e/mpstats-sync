from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import os
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_sheets_service():
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    logger.debug(f"Authorizing Google Sheets with {creds_path}")
    creds = service_account.Credentials.from_service_account_file(
        creds_path, scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)

