"""
Gmail utility functions for sending emails via Gmail API cu atașament PDF.
"""
from typing import Dict
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import base64
import os

def get_gmail_service():
    """
    Creează și returnează serviciul Gmail API.
    """
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    creds = None
    
    if os.path.exists('credentials/token_gmail.json'):
        creds = Credentials.from_authorized_user_file('credentials/token_gmail.json', SCOPES)
    
    if not creds or not creds.valid:
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow
        
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('credentials/token_gmail.json', 'w') as token:
            token.write(creds.to_json())
    
    service = build('gmail', 'v1', credentials=creds)
    return service

def send_invitation_with_ticket(recipient: str, guest_data: Dict, pdf_path: str) -> bool:
    """
    Trimite email cu invitația și biletul PDF atașat.
    """
    try:
        service = get_gmail_service()
        
        # Creează mesajul
        message = MIMEMultipart()
        message['to'] = recipient
        message['subject'] = f"Invitație Eveniment - Bilet {guest_data.get('Nume', '')} {guest_data.get('Prenume', '')}"
        
        # Corp email HTML
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4A90E2; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .footer {{ text-align: center; padding: 10px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Invitație Eveniment</h1>
                </div>
                <div class="content">
                    <p>Dragă <strong>{guest_data.get('Nume', '')} {guest_data.get('Prenume', '')}</strong>,</p>
                    <p>Vă invităm cu plăcere la evenimentul nostru!</p>
                    <p><strong>Locul dumneavoastră alocat:</strong> {guest_data.get('Loc', '')}</p>
                    <p>Găsiți atașat biletul dumneavoastră personalizat în format PDF.</p>
                    <p>Vă rugăm să prezentați biletul (imprimat sau pe telefon) la intrare, unde va fi scanat codul QR.</p>
                    <p>Vă așteptăm cu drag!</p>
                </div>
                <div class="footer">
                    <p>Pentru orice întrebări, vă rugăm să ne contactați.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        message.attach(MIMEText(html_body, 'html'))
        
        # Atașează PDF-ul
        if os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
                pdf_attachment.add_header('Content-Disposition', 'attachment', 
                                         filename=f"Bilet_{guest_data.get('Nume', '')}_{guest_data.get('Prenume', '')}.pdf")
                message.attach(pdf_attachment)
        
        # Encodează și trimite
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        send_message = {'raw': raw_message}
        
        service.users().messages().send(userId='me', body=send_message).execute()
        print(f"Email trimis cu succes către {recipient}")
        return True
        
    except Exception as e:
        print(f"Eroare la trimiterea emailului către {recipient}: {e}")
        return False

def send_invitation_email(recipient: str, subject: str, html_content: str) -> bool:
    """
    Trimite un email simplu (pentru compatibilitate cu codul existent).
    """
    try:
        service = get_gmail_service()
        
        message = MIMEMultipart()
        message['to'] = recipient
        message['subject'] = subject
        message.attach(MIMEText(html_content, 'html'))
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        send_message = {'raw': raw_message}
        
        service.users().messages().send(userId='me', body=send_message).execute()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
