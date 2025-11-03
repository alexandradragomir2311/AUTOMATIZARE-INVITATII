import os
import json
from typing import List, Dict
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import logging
import pickle
import os.path
import re
import hashlib
import secrets

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Configuration - Gmail API added for sending confirmation emails
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/documents.readonly',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]
DOCS_TEMPLATE_ID = '1GutvcK4_2pMSw2cccMliJ6JWp0cuvUUel1LP4IIOfuY'
SPREADSHEET_ID = '1-oAA8uUeDehcU-ckAHydsx8KujbXCWpZ0mMJIqWFoMg'
RANGE_NAME = "'INVITATII SI CONFIRMARI'!A2:J"

# ID-ul folderului din Google Drive unde sunt stocate invitațiile PDF
global FOLDER_ID
FOLDER_ID = os.getenv('INVITATII_FOLDER_ID', '1sKIpA-6LOSfGJP-FumxYuWtkQAtUew8e')

# Web App URL - URL-ul pentru confirmări
# RENDER cu PORT 465 SSL (în loc de 587 TLS)
WEBAPP_URL = os.getenv('WEBAPP_URL', 'https://automatizare-invitatii-1.onrender.com/confirm')

def get_credentials():
    """Get and refresh OAuth 2.0 credentials"""
    import base64
    
    creds = None
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if credentials are in environment variable (Render deployment)
    env_token = os.getenv('GOOGLE_TOKEN')
    env_creds = os.getenv('GOOGLE_CREDENTIALS')
    
    # Prioritate 1: GOOGLE_TOKEN (suficient pentru Render)
    if env_token:
        # Running on Render - use token from environment
        token_path = '/tmp/token.pickle'
        
        try:
            logger.info("🔍 Attempting to load GOOGLE_TOKEN from environment...")
            token_bytes = base64.b64decode(env_token)
            with open(token_path, 'wb') as f:
                f.write(token_bytes)
            
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
            
            # Verifică și reîmprospătează dacă e expirat
            if creds and creds.expired and creds.refresh_token:
                logger.info("🔄 Token expired, refreshing...")
                creds.refresh(Request())
                # Salvează token-ul reîmprospătat
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
            
            logger.info("✅ Loaded credentials from GOOGLE_TOKEN environment variable")
            return creds
        except Exception as e:
            logger.error(f"❌ Error loading GOOGLE_TOKEN: {e}")
            # NU continua, aruncă eroarea pentru debugging
            raise Exception(f"Failed to load GOOGLE_TOKEN: {e}")
    
    # Prioritate 2: GOOGLE_CREDENTIALS (pentru compatibilitate)
    if env_creds:
        logger.info("🔍 Using GOOGLE_CREDENTIALS...")
        creds_data = json.loads(env_creds)
        creds_path = '/tmp/credentials.json'
        token_path = '/tmp/token.pickle'
        
        with open(creds_path, 'w') as f:
            json.dump(creds_data, f)
        
        if env_token:
            token_bytes = base64.b64decode(env_token)
            with open(token_path, 'wb') as f:
                f.write(token_bytes)
    else:
        # Prioritate 3: Running locally
        logger.info("🔍 Running locally, using file credentials...")
        creds_path = os.path.join(current_dir, 'credentials', 'credentials.json')
        token_path = os.path.join(current_dir, 'credentials', 'token.pickle')

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("🔄 Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_path):
                raise FileNotFoundError(f"Credentials file not found at: {creds_path}")
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    return creds

def get_pdf_invitation(guest_name: str, filename: str = None) -> bytes:
    """Get personalized PDF invitation from Google Drive"""
    try:
        creds = get_credentials()
        drive_service = build('drive', 'v3', credentials=creds)
        
        # If exact filename is provided, use it
        if filename:
            logger.info(f"Searching for specific PDF: {filename} in folder {FOLDER_ID}")
            results = drive_service.files().list(
                q=f"name = '{filename}' and mimeType='application/pdf' and '{FOLDER_ID}' in parents",
                spaces='drive',
                fields='files(id, name)',
                pageSize=1
            ).execute()
            
            items = results.get('files', [])
            if items:
                pdf_id = items[0]['id']
                pdf_content = drive_service.files().get_media(fileId=pdf_id).execute()
                logger.info(f"Found PDF: {items[0]['name']}")
                return pdf_content
        
        # Search by guest name if no exact filename match
        pdf_name = f"INVITATIE_{guest_name.upper().replace(' ', '_')}.PDF"
        logger.info(f"Searching for PDF: {pdf_name} in folder {FOLDER_ID}")
        
        results = drive_service.files().list(
            q=f"name = '{pdf_name}' and mimeType='application/pdf' and '{FOLDER_ID}' in parents",
            spaces='drive',
            fields='files(id, name)',
            pageSize=1
        ).execute()
        
        items = results.get('files', [])
        if items:
            pdf_id = items[0]['id']
            pdf_content = drive_service.files().get_media(fileId=pdf_id).execute()
            logger.info(f"Found PDF: {items[0]['name']}")
            return pdf_content
            
        logger.warning(f"No PDF found with name: {pdf_name}")
        return None
        
    except Exception as e:
        logger.error(f"Error getting PDF invitation: {e}")
        return None

def get_invitation_text() -> str:
    """Get invitation text from Google Docs template"""
    try:
        creds = get_credentials()
        docs_service = build('docs', 'v1', credentials=creds)
        
        document = docs_service.documents().get(documentId=DOCS_TEMPLATE_ID).execute()
        
        text_content = ''
        for content in document.get('body').get('content'):
            if 'paragraph' in content:
                for element in content.get('paragraph').get('elements'):
                    if 'textRun' in element:
                        text_content += element.get('textRun').get('content')
        
        return text_content.strip()
        
    except Exception as e:
        logger.error(f"Error reading invitation template: {e}")
        return "Invitație la Concertul aniversar UNBR"

def is_valid_email(email: str) -> bool:
    """Validate email format and check for common misspellings"""
    if not email:
        return False
    
    # Basic format validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email.lower()):
        return False
    
    # List of invalid/misspelled domains
    invalid_domains = [
        'yaho.com', 'yaho.com', 'yahho.com',  # Yahoo misspellings
        'gmial.com', 'gmai.com', 'gmil.com',  # Gmail misspellings
        'hotmai.com', 'hotmal.com',  # Hotmail misspellings
        'outlok.com', 'outloo.com',  # Outlook misspellings
    ]
    
    # Extract domain
    domain = email.lower().split('@')[1] if '@' in email else ''
    
    # Check if domain is in invalid list
    if domain in invalid_domains:
        return False
    
    return True

def update_guest_status(email: str, mail_sent: bool = False, confirmation: str = None) -> bool:
    """Updates the guest status in the sheet with color formatting"""
    try:
        if not email:
            logger.error("Missing email address")
            return False

        creds = get_credentials()
        service = build('sheets', 'v4', credentials=creds)
        
        # Get sheet ID first
        spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        sheet_id = spreadsheet['sheets'][0]['properties']['sheetId']
        
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        
        rows = result.get('values', [])
        for idx, row in enumerate(rows):
            if len(row) > 4 and row[4] == email:
                # Update email status with emoji
                if mail_sent is not None:
                    email_range = f"'INVITATII SI CONFIRMARI'!G{idx+2}"
                    status_value = "Trimis ✅" if mail_sent else "Eroare ❌"
                    
                    # Update value
                    service.spreadsheets().values().update(
                        spreadsheetId=SPREADSHEET_ID,
                        range=email_range,
                        valueInputOption='RAW',
                        body={'values': [[status_value]]}
                    ).execute()
                    
                    # If error, color the cell red
                    if not mail_sent:
                        requests = [{
                            'updateCells': {
                                'range': {
                                    'sheetId': sheet_id,  # Use the actual sheet ID
                                    'startRowIndex': idx+1,
                                    'endRowIndex': idx+2,
                                    'startColumnIndex': 6,  # Column G
                                    'endColumnIndex': 7
                                },
                                'rows': [{
                                    'values': [{
                                        'userEnteredFormat': {
                                            'backgroundColor': {
                                                'red': 1.0,
                                                'green': 0.8,
                                                'blue': 0.8
                                            }
                                        }
                                    }]
                                }],
                                'fields': 'userEnteredFormat.backgroundColor'
                            }
                        }]
                        service.spreadsheets().batchUpdate(
                            spreadsheetId=SPREADSHEET_ID,
                            body={'requests': requests}
                        ).execute()
                    
                    logger.info(f"Updated email status for {email}: {status_value}")
                
                # Update participation status
                if confirmation:
                    confirm_range = f"'INVITATII SI CONFIRMARI'!H{idx+2}"
                    confirm_value = "✔ Da" if confirmation == "yes" else "❌ Nu"
                    
                    service.spreadsheets().values().update(
                        spreadsheetId=SPREADSHEET_ID,
                        range=confirm_range,
                        valueInputOption='RAW',
                        body={'values': [[confirm_value]]}
                    ).execute()
                    logger.info(f"Updated confirmation status for {email}: {confirm_value}")
                return True
                
        logger.warning(f"Could not find guest with email: {email}")
        return False
                
    except Exception as e:
        logger.error(f"Error updating sheet for {email}: {e}")
        return False

def mark_invalid_email(service, sheet_id: str, idx: int, email: str):
    """Marchează un email ca invalid în Google Sheet"""
    email_range = f"'INVITATII SI CONFIRMARI'!G{idx+2}"
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=email_range,
        valueInputOption='RAW',
        body={'values': [["Email invalid ❌"]]}
    ).execute()
    
    requests = [{
        'updateCells': {
            'range': {
                'sheetId': sheet_id,
                'startRowIndex': idx+1,
                'endRowIndex': idx+2,
                'startColumnIndex': 6,
                'endColumnIndex': 7
            },
            'rows': [{
                'values': [{
                    'userEnteredFormat': {
                        'backgroundColor': {
                            'red': 1.0,
                            'green': 0.8,
                            'blue': 0.8
                        }
                    }
                }]
            }],
            'fields': 'userEnteredFormat.backgroundColor'
        }
    }]
    service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={'requests': requests}
    ).execute()

def generate_unique_token(email: str, row_index: int) -> str:
    """Generate a unique token for each guest"""
    # Combină email, index și un secret pentru a crea un token unic
    secret = secrets.token_urlsafe(16)
    data = f"{email}_{row_index}_{secret}"
    return hashlib.sha256(data.encode()).hexdigest()[:32]  # Returnează primele 32 caractere

def get_guest_list() -> List[Dict[str, str]]:
    """Reads guest data from Google Sheets"""
    try:
        invitation_text = get_invitation_text()
        
        creds = get_credentials()
        service = build('sheets', 'v4', credentials=creds)
        
        # Get sheet ID first
        spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        sheet_id = spreadsheet['sheets'][0]['properties']['sheetId']
        
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        
        rows = result.get('values', [])
        guests = []
        
        # Process all rows
        for idx, row in enumerate(rows):
            row.extend([''] * (10 - len(row)))
            email = row[4].strip() if len(row) > 4 else ""
            
            if email:  # Process only if email exists
                if is_valid_email(email):
                    # Generate or retrieve token for this guest
                    existing_token = row[9] if len(row) > 9 and row[9] else None
                    
                    if not existing_token:
                        # Generate new token
                        token = generate_unique_token(email, idx)
                        
                        # Save token to column J (index 9)
                        token_range = f"'INVITATII SI CONFIRMARI'!J{idx+2}"
                        service.spreadsheets().values().update(
                            spreadsheetId=SPREADSHEET_ID,
                            range=token_range,
                            valueInputOption='RAW',
                            body={'values': [[token]]}
                        ).execute()
                    else:
                        token = existing_token
                    
                    # Create guest object for valid emails
                    guest = {
                        'nume_complet': row[0],
                        'institutie': row[1],
                        'functie': row[2],
                        'gen': row[3],
                        'email': email,
                        'pdf_invitatie': row[5],
                        'email_trimis': row[6],
                        'confirmare': row[7],
                        'raspuns': row[8],
                        'invitation_text': invitation_text,
                        'token': token
                    }
                    
                    # Add confirmation URLs with token
                    confirm_url = f"{WEBAPP_URL}?token={token}"
                    decline_url = f"{WEBAPP_URL}?token={token}&resp=nu"
                    guest['confirm_url'] = confirm_url
                    guest['decline_url'] = decline_url
                    guests.append(guest)
                    
                    # Reset status for valid emails (will be updated when email is sent)
                    email_range = f"'INVITATII SI CONFIRMARI'!G{idx+2}"
                    service.spreadsheets().values().update(
                        spreadsheetId=SPREADSHEET_ID,
                        range=email_range,
                        valueInputOption='RAW',
                        body={'values': [[""]]}
                    ).execute()
                else:
                    # Mark invalid emails
                    email_range = f"'INVITATII SI CONFIRMARI'!G{idx+2}"
                    service.spreadsheets().values().update(
                        spreadsheetId=SPREADSHEET_ID,
                        range=email_range,
                        valueInputOption='RAW',
                        body={'values': [["Email invalid ❌"]]}
                    ).execute()
                    
                    # Apply red background for invalid emails
                    requests = [{
                        'updateCells': {
                            'range': {
                                'sheetId': sheet_id,
                                'startRowIndex': idx+1,
                                'endRowIndex': idx+2,
                                'startColumnIndex': 6,
                                'endColumnIndex': 7
                            },
                            'rows': [{
                                'values': [{
                                    'userEnteredFormat': {
                                        'backgroundColor': {
                                            'red': 1.0,
                                            'green': 0.8,
                                            'blue': 0.8
                                        }
                                    }
                                }]
                            }],
                            'fields': 'userEnteredFormat.backgroundColor'
                        }
                    }]
                    service.spreadsheets().batchUpdate(
                        spreadsheetId=SPREADSHEET_ID,
                        body={'requests': requests}
                    ).execute()
            else:
                # Mark rows without email as "Lipsă email ⚠️"
                email_range = f"'INVITATII SI CONFIRMARI'!G{idx+2}"
                service.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=email_range,
                    valueInputOption='RAW',
                    body={'values': [["Lipsă email ⚠️"]]}
                ).execute()
                
                # Apply yellow background for missing emails
                requests = [{
                    'updateCells': {
                        'range': {
                            'sheetId': sheet_id,
                            'startRowIndex': idx+1,
                            'endRowIndex': idx+2,
                            'startColumnIndex': 6,
                            'endColumnIndex': 7
                        },
                        'rows': [{
                            'values': [{
                                'userEnteredFormat': {
                                    'backgroundColor': {
                                        'red': 1.0,
                                        'green': 1.0,
                                        'blue': 0.8
                                    }
                                }
                            }]
                        }],
                        'fields': 'userEnteredFormat.backgroundColor'
                    }
                }]
                service.spreadsheets().batchUpdate(
                    spreadsheetId=SPREADSHEET_ID,
                    body={'requests': requests}
                ).execute()
        
        logger.info(f"Found {len(guests)} guests with valid email addresses")
        return guests
        
    except Exception as e:
        logger.error(f"Error reading guest list: {e}")
        return []