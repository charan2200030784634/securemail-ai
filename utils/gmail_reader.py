import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    creds = None
    
    # Detect environment
    if os.path.exists('/etc/secrets/credentials.json'):
        credentials_path = '/etc/secrets/credentials.json'
        token_path = '/tmp/token.json'
    else:
        credentials_path = 'credentials.json'
        token_path = 'token.json'
    
    # Load token
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    # If no creds
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save token
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service


def read_emails():
    service = get_gmail_service()
    
    results = service.users().messages().list(
        userId='me',
        maxResults=10
    ).execute()
    
    messages = results.get('messages', [])

    emails = []

    for msg in messages:
        txt = service.users().messages().get(
            userId='me',
            id=msg['id']
        ).execute()

        payload = txt['payload']
        headers = payload.get("headers")

        subject = ""
        sender = ""

        for d in headers:
            if d['name'] == 'Subject':
                subject = d['value']
            if d['name'] == 'From':
                sender = d['value']

        emails.append({
            "subject": subject,
            "sender": sender
        })

    return emails