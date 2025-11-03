"""
Utilități pentru trimiterea de emailuri prin serverul SMTP personalizat UNBR.
"""
import smtplib
import os
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.utils import formataddr
from typing import Dict, Optional
from email_config import EmailConfig

def get_email_config() -> EmailConfig:
    """
    Returnează configurația de email. Încearcă să încarce parola din fișier,
    apoi din variabilele de mediu.
    """
    # Încearcă să încarce din fișier
    config = EmailConfig.load_from_file()
    
    # Dacă nu există parolă în fișier, încearcă din variabilele de mediu
    if not config.email_password:
        config = EmailConfig.load_from_env()
    
    # Dacă încă nu există parolă, solicită utilizatorului
    if not config.email_password:
        print("ATENȚIE: Nu am găsit parola pentru emailul evenimente@unbr.ro")
        print("Opțiuni pentru setarea parolei:")
        print("1. Creează fișierul 'credentials/email_credentials.txt' și pune parola acolo")
        print("2. Setează variabila de mediu EMAIL_PASSWORD")
        print("3. Introdu parola manual (nesigur)")
        
        choice = input("Alege opțiunea (1/2/3): ").strip()
        
        if choice == "3":
            config.email_password = input("Introdu parola pentru evenimente@unbr.ro: ").strip()
        elif choice == "1":
            # Creează directorul credentials dacă nu există
            os.makedirs('credentials', exist_ok=True)
            password = input("Introdu parola pentru evenimente@unbr.ro: ").strip()
            with open('credentials/email_credentials.txt', 'w', encoding='utf-8') as f:
                f.write(password)
            config.email_password = password
            print("Parolă salvată în credentials/email_credentials.txt")
    
    return config

def is_valid_email_smtp(email: str) -> bool:
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

def update_guest_status_smtp(email: str, mail_sent: bool = False, confirmation: str = None) -> bool:
    """Updates the guest status in the sheet with color formatting - SMTP version"""
    try:
        if not email:
            print("Missing email address")
            return False

        # Import doar Google Sheets API, nu Gmail
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
                    status_value = "Trimis ✅ (SMTP)" if mail_sent else "Eroare ❌"
                    
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
                                    'sheetId': sheet_id,
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
                    
                    print(f"Updated email status for {email}: {status_value}")
                
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
                    print(f"Updated confirmation status for {email}: {confirm_value}")
                return True
                
        print(f"Could not find guest with email: {email}")
        return False
                
    except Exception as e:
        print(f"Error updating sheet for {email}: {e}")
        return False

def send_email_smtp(recipient: str, subject: str, html_content: str, 
                   attachments: Optional[list] = None, email_type: str = "general") -> bool:
    """
    Trimite email prin serverul SMTP UNBR și salvează în foldere organizate.
    
    Args:
        recipient: Adresa de email a destinatarului
        subject: Subiectul emailului
        html_content: Conținutul HTML al emailului
        attachments: Lista de atașamente (tuple cu (cale_fișier, nume_afișat))
        email_type: Tipul emailului pentru organizare ("invitatie", "confirmare", "bilet")
    
    Returns:
        bool: True dacă emailul a fost trimis cu succes
    """
    try:
        config = get_email_config()
        
        if not config.email_password:
            print("Eroare: Nu am putut obține parola pentru email")
            return False
        
        # Creează mesajul
        message = MIMEMultipart('related')
        message['From'] = formataddr(('Evenimente UNBR', config.email_address))
        message['To'] = recipient
        message['Subject'] = subject
        
        # Adaugă conținutul HTML
        message.attach(MIMEText(html_content, 'html', 'utf-8'))
        
        # Adaugă atașamentele dacă există
        if attachments:
            for file_path, display_name in attachments:
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        attachment = MIMEApplication(f.read())
                        attachment.add_header('Content-Disposition', 'attachment', 
                                            filename=display_name)
                        message.attach(attachment)
        
        # Conectează la serverul SMTP și trimite emailul
        with smtplib.SMTP(config.smtp_server, config.smtp_port) as server:
            if config.smtp_use_tls:
                server.starttls()  # Activează criptarea TLS
            
            server.login(config.email_address, config.email_password)
            server.send_message(message)
        
        print(f"Email trimis cu succes către {recipient} prin SMTP {config.smtp_server}")
        
        # Salvează emailul în foldere organizate
        if config.organize_by_folders:
            try:
                from email_organization import save_sent_email_to_folder
                save_sent_email_to_folder(message, config, email_type)
            except Exception as e:
                print(f"⚠️  Email trimis dar nu s-a salvat în foldere: {e}")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"Eroare de autentificare SMTP: {e}")
        print("Verifică că parola este corectă și că autentificarea externă este activată")
        return False
    except smtplib.SMTPException as e:
        print(f"Eroare SMTP: {e}")
        return False
    except Exception as e:
        print(f"Eroare la trimiterea emailului către {recipient}: {e}")
        return False

def send_email2_smtp(guest: Dict[str, str]) -> bool:
    """
    Versiunea SMTP a funcției send_email2 din sheets_utils.py.
    Trimite email cu invitația și logo-ul UNBR, cu același format ca originalul.
    """
    try:
        email = guest.get('email', '').strip()
        
        if not email:
            print("Missing email address")
            return False
            
        if not is_valid_email_smtp(email):
            print(f"Invalid email format: {email}")
            update_guest_status_smtp(email, False)
            return False
        
        config = get_email_config()
        
        if not config.email_password:
            print("Eroare: Nu am putut obține parola pentru email")
            return False
        
        # Determină formula de adresare bazată pe gen
        gen = guest.get('gen', '').strip().upper()
        if gen == 'F':
            gender_title = "Doamnă"
        elif gen == 'M':
            gender_title = "Domn"
        else:
            gender_title = "Doamnă"  # Default to Doamnă if gender not specified
        
        # Creează mesajul cu același format ca originalul
        message = MIMEMultipart('related')
        message['From'] = formataddr(('Evenimente UNBR', config.email_address))
        message['To'] = guest['email']
        message['Subject'] = 'Invitație UNBR Concert aniversar, 24 noiembrie 2025'
        
        # Același text de invitație ca în originalul
        invitation_text = """Vă transmitem atașat invitația Președintelui UNBR, avocat Traian Briciu, de a participa la <strong>concertul omagial</strong> organizat de UNBR în data de <strong>24 noiembrie 2025</strong>, <strong>ora 19:30</strong>, la Ateneul Român.<br><br>Vă rugăm să ne comunicați până la <strong>10 noiembrie 2025</strong> dacă agenda vă permite să luați parte la acest eveniment deosebit. În cazul unui răspuns afirmativ, vă rugăm să precizați dacă preferați o rezervare pentru unul sau două locuri.<br><br>Rămânem la dispoziția dumneavoastră pentru orice informații suplimentare și detalii necesare."""
        
        # Același CSS ca în originalul
        css = """
            body { 
                font-family: Arial, sans-serif; 
                line-height: 1.6; 
                color: #333;
                margin: 0;
                padding: 0;
            }
            .container { 
                max-width: 600px; 
                margin: 0 auto; 
                padding: 30px;
                background-color: #ffffff;
            }
            .content {
                margin-bottom: 30px;
                text-align: left;
                padding-left: 0;
            }
            .subject {
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 25px;
                color: #000;
                text-align: left;
            }
            .greeting {
                margin-bottom: 20px;
                font-weight: normal;
                text-align: left;
                padding-left: 0;
            }
            .invitation-text {
                margin-bottom: 30px;
                text-align: left;
                line-height: 1.8;
                padding-left: 0;
            }
            .buttons {
                text-align: center;
                margin: 30px 0;
            }
            .button { 
                display: inline-block; 
                padding: 14px 32px; 
                margin: 10px; 
                text-decoration: none; 
                border-radius: 6px; 
                color: #fff !important; 
                font-weight: bold;
                font-size: 17px;
                border: none;
                box-shadow: 0 2px 8px rgba(80,40,20,0.08);
                transition: background 0.3s, color 0.3s, box-shadow 0.3s;
                letter-spacing: 0.5px;
                background: #7c3f00; /* fallback solid for maro */
            }
            .confirm { 
                background: linear-gradient(90deg, #7c3f00 0%, #a9744f 100%) !important; /* maro elegant */
                border: 1.5px solid #7c3f00;
                color: #fff !important;
            }
            .decline { 
                background: linear-gradient(90deg, #800020 0%, #b22234 100%) !important; /* bordo elegant */
                border: 1.5px solid #800020;
                color: #fff !important;
            }
            .confirm:hover { 
                background: linear-gradient(90deg, #a9744f 0%, #7c3f00 100%) !important;
                color: #fffbe6 !important;
                box-shadow: 0 4px 16px rgba(124,63,0,0.15);
            }
            .decline:hover { 
                background: linear-gradient(90deg, #b22234 0%, #800020 100%) !important;
                color: #fff0f3 !important;
                box-shadow: 0 4px 16px rgba(128,0,32,0.15);
            }
            .signature {
                margin-top: 40px;
                padding-top: 20px;
                line-height: 1.4;
            }
            .name {
                font-weight: bold;
                color: #333;
                font-size: 15px;
                margin-bottom: 5px;
            }
            .title {
                color: #333;
                font-size: 14px;
                margin-bottom: 5px;
            }
            .institution { 
                color: #333;
                font-size: 14px;
                margin-bottom: 15px;
            }
            .logo { 
                max-width: 120px;
                display: block;
                margin: 10px 0;
            }
            .address-header {
                color: #333;
                font-size: 14px;
                margin: 10px 0 5px 0;
            }
            .address {
                color: #333;
                font-size: 14px;
                margin: 3px 0;
            }
            .contact {
                color: #333;
                font-size: 14px;
                margin: 3px 0;
            }
            strong {
                color: #000;
                font-weight: bold;
            }
        """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                {css}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="content">
                    <p class="greeting">Bună ziua, {gender_title} {guest.get('nume_complet', '')},</p>
                    <div class="invitation-text" style="margin-top: 20px; white-space: pre-line;">
                        {invitation_text}
                    </div>
                    <div class="buttons">
                        <a href="{guest['confirm_url']}" class="button confirm">
                            Confirm participarea
                        </a>
                        <a href="{guest['decline_url']}" class="button decline">
                            Nu pot participa
                        </a>
                    </div>
                    <div class="signature">
                        <p class="regards">Cu stimă,</p>
                        <p class="name">Alexandra-Nicoleta DRAGOMIR</p>
                        <p class="title">Consultant Colaborator în cadrul</p>
                        <p class="institution">Uniunii Naționale a Barourilor din România</p>
                        <img src="cid:logo" alt="UNBR Logo" class="logo"/>
                        <p class="address-header">București, Palatul de Justiție</p>
                        <p class="address">Splaiul Independenței nr. 5, sector 5</p>
                        <p class="contact">Tel +40213134875, +40213160739, +40213160740</p>
                        <p class="contact">Fax +40213134880</p>
                        <p class="contact">Mobil +4740318791</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg_html = MIMEText(html, 'html', 'utf-8')
        message.attach(msg_html)
        
        # Attach UNBR logo
        try:
            with open('static/logo.png', 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-ID', '<logo>')
                message.attach(img)
        except FileNotFoundError:
            print("Warning: Logo file static/logo.png not found, sending email without logo")
        
        # Atașează PDF-ul invitației
        try:
            import os
            import glob
            from email.mime.application import MIMEApplication
            
            # Extrage nume și prenume din nume_complet
            nume_complet = guest.get('nume_complet', '').strip()
            parts = nume_complet.split()
            
            if len(parts) >= 2:
                # Presupunem că ultimul cuvânt e prenumele, restul e numele
                prenume = parts[-1].upper()
                nume = '_'.join(parts[:-1]).upper()
                
                # Caută PDF-ul cu diferite pattern-uri posibile
                pdf_patterns = [
                    f"C:/Users/40740/Desktop/EVENIMENT INVITATII/output/invitatie_{prenume}_{nume}.pdf",
                    f"C:/Users/40740/Desktop/EVENIMENT INVITATII/output/invitatie_{nume}_{prenume}.pdf",
                    f"C:/Users/40740/Desktop/EVENIMENT INVITATII/output/invitatie_{parts[0].upper()}_{parts[-1].upper()}.pdf"
                ]
                
                pdf_files = []
                for pattern in pdf_patterns:
                    pdf_files = glob.glob(pattern)
                    if pdf_files:
                        break
                
                if pdf_files:
                    pdf_path = pdf_files[0]
                    with open(pdf_path, 'rb') as pdf_file:
                        pdf_attachment = MIMEApplication(pdf_file.read(), _subtype='pdf')
                        pdf_attachment.add_header('Content-Disposition', 'attachment', 
                                                filename=f'Invitatie_UNBR_{nume_complet.replace(" ", "_")}.pdf')
                        message.attach(pdf_attachment)
                    print(f"✓ PDF invitație atașat: {os.path.basename(pdf_path)}")
                else:
                    print(f"⚠️  PDF invitație nu a fost găsit pentru {nume_complet}")
            else:
                print(f"⚠️  Nume invalid: {nume_complet}")
        except Exception as e:
            print(f"⚠️  Eroare la atașarea PDF-ului: {e}")
        
        # Conectează la serverul SMTP și trimite emailul
        with smtplib.SMTP(config.smtp_server, config.smtp_port) as server:
            if config.smtp_use_tls:
                server.starttls()
            
            server.login(config.email_address, config.email_password)
            server.send_message(message)
        
        print(f"Email trimis cu succes către {guest['email']} prin SMTP {config.smtp_server}")
        
        # Salvează emailul în foldere organizate
        if config.organize_by_folders:
            try:
                from email_organization import save_sent_email_to_folder
                save_sent_email_to_folder(message, config, "invitatie")
                print(f"📁 Email salvat în folderul '{config.concert_folder_name}'")
            except Exception as e:
                print(f"⚠️  Email trimis dar nu s-a salvat în foldere: {e}")
        
        # Update sheet status - versiunea SMTP
        update_guest_status_smtp(guest['email'], True)
        print(f"Successfully sent invitation to {guest['email']} via UNBR SMTP")
        return True
            
    except Exception as e:
        print(f"Error sending email to {guest['email']}: {e}")
        update_guest_status_smtp(guest.get('email', ''), False)
        return False

def send_invitation_with_ticket(recipient: str, guest_data: Dict, pdf_path: str) -> bool:
    """
    Trimite email cu invitația și biletul PDF atașat prin SMTP.
    """
    subject = f"Invitație Eveniment - Bilet {guest_data.get('Nume', '')} {guest_data.get('Prenume', '')}"
    
    # Corp email HTML
    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #003366; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ padding: 30px; background-color: #f9f9f9; border-radius: 0 0 10px 10px; }}
            .highlight {{ background-color: #e6f3ff; padding: 15px; border-left: 4px solid #003366; margin: 20px 0; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 0.9em; }}
            .logo {{ font-size: 1.5em; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">UNBR - Evenimente</div>
                <h1>Invitație Eveniment</h1>
            </div>
            <div class="content">
                <p>Stimată/Stimat <strong>{guest_data.get('Nume', '')} {guest_data.get('Prenume', '')}</strong>,</p>
                
                <p>Vă invităm cu mare plăcere la evenimentul nostru!</p>
                
                <div class="highlight">
                    <p><strong>📍 Locul dumneavoastră alocat:</strong> {guest_data.get('Loc', 'Nu este specificat')}</p>
                    <p><strong>🎫 Numărul biletului:</strong> {guest_data.get('ID', '')}</p>
                </div>
                
                <p>Găsiți atașat biletul dumneavoastră personalizat în format PDF.</p>
                
                <p><strong>Instrucțiuni importante:</strong></p>
                <ul>
                    <li>Vă rugăm să prezentați biletul (imprimat sau pe telefon) la intrare</li>
                    <li>Codul QR de pe bilet va fi scanat pentru validare</li>
                    <li>Păstrați biletul în siguranță până la eveniment</li>
                </ul>
                
                <p>Vă așteptăm cu drag la acest eveniment special!</p>
                
                <p>Cu stimă,<br><strong>Echipa Evenimente UNBR</strong></p>
            </div>
            <div class="footer">
                <p>Pentru orice întrebări, vă rugăm să ne contactați la: <strong>evenimente@unbr.ro</strong></p>
                <p>Universitatea Națională de Apărare "Carol I"</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Pregătește atașamentul
    attachments = []
    if os.path.exists(pdf_path):
        display_name = f"Bilet_{guest_data.get('Nume', '')}_{guest_data.get('Prenume', '')}.pdf"
        attachments.append((pdf_path, display_name))
    
    return send_email_smtp(recipient, subject, html_body, attachments)

def send_invitation_email(recipient: str, subject: str, html_content: str) -> bool:
    """
    Trimite un email simplu prin SMTP (pentru compatibilitate cu codul existent).
    """
    return send_email_smtp(recipient, subject, html_content)

def test_email_connection() -> bool:
    """
    Testează conexiunea la serverul SMTP pentru a verifica configurația.
    """
    try:
        config = get_email_config()
        
        if not config.email_password:
            print("Nu pot testa conexiunea fără parolă")
            return False
        
        print(f"Testez conexiunea la {config.smtp_server}:{config.smtp_port}...")
        
        with smtplib.SMTP(config.smtp_server, config.smtp_port) as server:
            if config.smtp_use_tls:
                server.starttls()
            
            server.login(config.email_address, config.email_password)
            print("✓ Conexiunea SMTP a fost testată cu succes!")
            return True
            
    except smtplib.SMTPAuthenticationError as e:
        print(f"✗ Eroare de autentificare: {e}")
        print("Verifică parola și setările contului")
        return False
    except Exception as e:
        print(f"✗ Eroare la testarea conexiunii: {e}")
        return False

def send_invitation_with_ticket(recipient: str, guest_data: Dict, pdf_path: str) -> bool:
    """
    Trimite email cu invitația și biletul PDF atașat prin SMTP.
    Funcție de compatibilitate pentru main.py și ticket generation.
    """
    subject = f"Invitație Eveniment - Bilet {guest_data.get('Nume', '')} {guest_data.get('Prenume', '')}"
    
    # Corp email HTML pentru bilete
    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #003366; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ padding: 30px; background-color: #f9f9f9; border-radius: 0 0 10px 10px; }}
            .highlight {{ background-color: #e6f3ff; padding: 15px; border-left: 4px solid #003366; margin: 20px 0; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 0.9em; }}
            .logo {{ font-size: 1.5em; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">UNBR - Evenimente</div>
                <h1>Biletul Dumneavoastră</h1>
            </div>
            <div class="content">
                <p>Stimată/Stimat <strong>{guest_data.get('Nume', '')} {guest_data.get('Prenume', '')}</strong>,</p>
                
                <p>Vă mulțumim pentru confirmarea participării!</p>
                
                <div class="highlight">
                    <p><strong>📍 Locul dumneavoastră alocat:</strong> {guest_data.get('Loc', 'Nu este specificat')}</p>
                    <p><strong>🎫 Numărul biletului:</strong> {guest_data.get('ID', '')}</p>
                </div>
                
                <p>Găsiți atașat biletul dumneavoastră personalizat în format PDF.</p>
                
                <p><strong>Instrucțiuni importante:</strong></p>
                <ul>
                    <li>Vă rugăm să prezentați biletul (imprimat sau pe telefon) la intrare</li>
                    <li>Codul QR de pe bilet va fi scanat pentru validare</li>
                    <li>Păstrați biletul în siguranță până la eveniment</li>
                </ul>
                
                <p>Vă așteptăm cu drag la acest eveniment special!</p>
                
                <p>Cu stimă,<br><strong>Echipa Evenimente UNBR</strong></p>
            </div>
            <div class="footer">
                <p>Pentru orice întrebări, vă rugăm să ne contactați la: <strong>evenimente@unbr.ro</strong></p>
                <p>Universitatea Națională de Apărare "Carol I"</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Pregătește atașamentul
    attachments = []
    if pdf_path and os.path.exists(pdf_path):
        display_name = f"Bilet_{guest_data.get('Nume', '')}_{guest_data.get('Prenume', '')}.pdf"
        attachments.append((pdf_path, display_name))
    
    return send_email_smtp(recipient, subject, html_body, attachments, "bilet")

def send_invitation_email(recipient: str, subject: str, html_content: str) -> bool:
    """
    Trimite un email simplu prin SMTP (pentru compatibilitate cu codul existent).
    """
    return send_email_smtp(recipient, subject, html_content)