from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

from config import SCOPES, PROCESSED_LABEL

SECRETS_DIR = "secrets"
TOKEN_PATH = os.path.join(SECRETS_DIR, "token.json")
CREDS_PATH = os.path.join(SECRETS_DIR,
"credentials.json")

print("Looking for credentials at:", CREDS_PATH)

def get_gmail_service():
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH,
SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDS_PATH, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def get_or_create_label(service):
    labels = service.users().labels().list(userId="me").execute()["labels"]

    for label in labels:
        if label["name"] == PROCESSED_LABEL:
            return label["id"]

    label_body = {
        "name": PROCESSED_LABEL,
        "labelListVisibility": "labelShow",
        "messageListVisibility": "show"
    }

    label = service.users().labels().create(
        userId="me", body=label_body
    ).execute()

    return label["id"]


def fetch_unprocessed_messages(service, max_results=10):
    response = service.users().messages().list(
        userId="me",
        labelIds=["SENT"],   # only mail in Sent
        q=f"-label:{PROCESSED_LABEL}",  # exclude processed
        maxResults=max_results
    ).execute()

    return response.get("messages", [])


def mark_as_processed(service, msg_id, label_id):
    service.users().messages().modify(
        userId="me",
        id=msg_id,
        body={
            "addLabelIds": [label_id],
        }
    ).execute()
