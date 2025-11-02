"""
Script pentru resetarea statusului emailurilor în Google Sheets pentru testare.
"""
from smtp_utils import update_guest_status_smtp

def reset_email_status():
    """Resetează statusul pentru testare"""
    print("Resetez statusul pentru testare...")
    
    # Lista emailurilor de resetat (adaugă aici emailurile pentru test)
    test_emails = [
        "alexandradragomir23@yahoo.com"
    ]
    
    for email in test_emails:
        # Actualizează statusul în Google Sheets ca netrimi
        try:
            # Import doar Google Sheets API
            from googleapiclient.discovery import build
            import pickle
            import os.path
            from google.auth.transport.requests import Request
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.oauth2.credentials import Credentials
            import json
            
            SPREADSHEET_ID = '1-oAA8uUeDehcU-ckAHydsx8KujbXCWpZ0mMJIqWFoMg'
            RANGE_NAME = "'INVITATII SI CONFIRMARI'!A2:J"
            SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
            
            # Get credentials for Sheets only
            creds = None
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Check if credentials are in environment variable (Render deployment)
            env_creds = os.getenv('GOOGLE_CREDENTIALS')
            env_token = os.getenv('GOOGLE_TOKEN')
            
            if env_creds:
                # Running on Render - use environment variables
                creds_data = json.loads(env_creds)
                creds_path = '/tmp/credentials.json'
                token_path = '/tmp/token.pickle'
                
                with open(creds_path, 'w') as f:
                    json.dump(creds_data, f)
                
                # Decode and save token if available
                if env_token:
                    import base64
                    token_bytes = base64.b64decode(env_token)
                    with open(token_path, 'wb') as f:
                        f.write(token_bytes)
            else:
                # Running locally
                creds_path = os.path.join(current_dir, 'credentials', 'credentials.json')
                token_path = os.path.join(current_dir, 'credentials', 'token.pickle')

            if os.path.exists(token_path):
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(creds_path):
                        print(f"Credentials file not found at: {creds_path}")
                        return False
                    flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)

            service = build('sheets', 'v4', credentials=creds)
            
            result = service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=RANGE_NAME
            ).execute()
            
            rows = result.get('values', [])
            for idx, row in enumerate(rows):
                if len(row) > 4 and row[4] == email:
                    # Resetează statusul emailului
                    email_range = f"'INVITATII SI CONFIRMARI'!G{idx+2}"
                    
                    service.spreadsheets().values().update(
                        spreadsheetId=SPREADSHEET_ID,
                        range=email_range,
                        valueInputOption='RAW',
                        body={'values': [[""]]}  # Resetează la gol
                    ).execute()
                    
                    print(f"✓ Resetat statusul pentru {email}")
                    break
            else:
                print(f"✗ Nu am găsit emailul {email}")
                
        except Exception as e:
            print(f"✗ Eroare la resetarea statusului pentru {email}: {e}")

if __name__ == "__main__":
    reset_email_status()
    print("\nAcum poți rula din nou: python send_invitations.py")