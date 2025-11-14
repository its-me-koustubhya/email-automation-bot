import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from config.settings import CREDENTIALS_FILE, TOKEN_FILE, GMAIL_SCOPES

# If modifying these scopes, delete the file token.json.
SCOPES = GMAIL_SCOPES


def get_gmail_service():
  """
    Authenticates with Gmail API and returns service object.
    
    Returns:
        service: Authenticated Gmail API service
    """

  creds = None
  if os.path.exists(TOKEN_FILE):
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          CREDENTIALS_FILE, SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(TOKEN_FILE, "w") as token:
      token.write(creds.to_json())

  service = build("gmail", "v1", credentials=creds)  

  return service
