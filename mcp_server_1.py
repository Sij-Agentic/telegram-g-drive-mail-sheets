from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables
load_dotenv()

# Gmail API setup
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
TOKEN_PICKLE = 'token.pickle'
CLIENT_SECRET_FILE = os.getenv('GOOGLE_CLIENT_SECRET_FILE', 'client_secret.json')

def get_gmail_service():
    creds = None
    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PICKLE, 'wb') as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

mcp = FastMCP("Gmail")

@mcp.tool()
def send_email(recipient: str, subject: str, body: str) -> str:
    """Send an email using Gmail API. Usage: send_email|recipient="example@example.com"|subject="Test"|body="Hello" """
    try:
        service = get_gmail_service()
        message = MIMEMultipart()
        message['to'] = recipient
        message['subject'] = subject
        message.attach(MIMEText(body, 'plain'))
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        return f"Email sent to {recipient}"
    except Exception as e:
        return f"Error sending email: {str(e)}"

if __name__ == "__main__":
    print("STARTING Gmail Server on port 8001")
    mcp.run(transport="sse")