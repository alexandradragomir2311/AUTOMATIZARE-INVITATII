"""
Funcții pentru organizarea emailurilor prin IMAP în folderul evenimente@unbr.ro
"""
import imaplib
import email
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email_config import EmailConfig
from typing import Optional

def get_imap_connection(config: EmailConfig) -> Optional[imaplib.IMAP4_SSL]:
    """Creează conexiune IMAP la serverul UNBR"""
    try:
        # Conectează la serverul IMAP
        mail = imaplib.IMAP4_SSL(config.imap_server, config.imap_port)
        mail.login(config.email_address, config.email_password)
        return mail
    except Exception as e:
        print(f"Eroare conectare IMAP: {e}")
        return None

def create_concert_folder(config: EmailConfig) -> bool:
    """Creează folderele pentru Concert 2025 dacă nu există"""
    try:
        mail = get_imap_connection(config)
        if not mail:
            return False
        
        # Lista de foldere de creat
        folders_to_create = [
            config.concert_folder_name,  # Invitatii Transmise Concert 2025
            config.confirmations_folder_name  # Confirmari Concert 2025
        ]
        
        status, existing_folders = mail.list()
        
        for folder_name in folders_to_create:
            folder_exists = False
            if status == 'OK':
                for folder in existing_folders:
                    if folder_name.encode() in folder:
                        folder_exists = True
                        break
            
            if not folder_exists:
                # Creează folderul
                status_create, response = mail.create(f'"{folder_name}"')
                if status_create == 'OK':
                    print(f"✓ Folderul '{folder_name}' a fost creat cu succes")
                else:
                    print(f"✗ Eroare la crearea folderului: {response}")
            else:
                print(f"✓ Folderul '{folder_name}' există deja")
        
        mail.logout()
        return True
        
    except Exception as e:
        print(f"Eroare la crearea folderelor: {e}")
        return False

def save_sent_email_to_folder(message: MIMEMultipart, config: EmailConfig, email_type: str = "invitatie") -> bool:
    """
    Salvează emailul trimis în folderul specific în funcție de tip
    
    Args:
        message: Mesajul email trimis
        config: Configurația email
        email_type: Tipul emailului ("invitatie", "confirmare", "declinare", "bilet")
    """
    try:
        mail = get_imap_connection(config)
        if not mail:
            return False
        
        # Adaugă headers pentru identificare
        message['X-Concert-Type'] = email_type
        message['X-Concert-Event'] = "Concert Aniversar UNBR 2025"
        message['X-Concert-Date'] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Convertește mesajul la format IMAP
        email_string = message.as_string()
        
        # Determină folderul în funcție de tipul emailului
        if email_type in ["confirmare", "declinare"]:
            folder_name = config.confirmations_folder_name
        else:
            folder_name = config.concert_folder_name
        
        # Salvează în folderul specific
        try:
            mail.append(f'"{folder_name}"', '\\Seen', None, email_string.encode('utf-8'))
            print(f"✓ Email salvat în folderul '{folder_name}'")
        except Exception as e:
            print(f"⚠️  Nu s-a putut salva în folderul '{folder_name}': {e}")
        
        mail.logout()
        return True
        
    except Exception as e:
        print(f"Eroare la salvarea emailului: {e}")
        return False

def create_confirmation_response_email(guest_name: str, response: str, guest_email: str) -> MIMEMultipart:
    """
    Creează emailul automat de răspuns pentru confirmări/declinări
    
    Args:
        guest_name: Numele invitatului
        response: "confirmare" sau "declinare"
        guest_email: Emailul invitatului
    """
    message = MIMEMultipart()
    message['From'] = 'Evenimente UNBR <evenimente@unbr.ro>'
    message['To'] = guest_email
    message['X-Auto-Response-Suppress'] = 'All'  # Previne auto-reply loops
    
    if response == "confirmare":
        message['Subject'] = 'Confirmare primită - Concert Aniversar UNBR'
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2e7d32; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 30px; background-color: #f1f8e9; border-radius: 0 0 10px 10px; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Confirmare Primită!</h1>
                </div>
                <div class="content">
                    <p>Stimată/Stimat <strong>{guest_name}</strong>,</p>
                    
                    <p>Vă mulțumim pentru confirmarea participării la <strong>Concertul Aniversar UNBR din 24 noiembrie 2025</strong>!</p>
                    
                    <p><strong>Confirmarea dumneavoastră a fost înregistrată cu succes.</strong></p>
                    
                    <p>În curând veți primi:</p>
                    <ul>
                        <li>📧 Email cu biletul personalizat</li>
                        <li>🎫 Codul QR pentru intrare</li>
                        <li>📍 Detalii complete despre eveniment</li>
                    </ul>
                    
                    <p>Pentru orice întrebări, nu ezitați să ne contactați.</p>
                    
                    <p>Cu stimă,<br><strong>Echipa Evenimente UNBR</strong></p>
                </div>
                <div class="footer">
                    <p>Universitatea Națională de Apărare "Carol I"</p>
                    <p>📧 evenimente@unbr.ro | 📞 +40213134875</p>
                </div>
            </div>
        </body>
        </html>
        """
    else:  # declinare
        message['Subject'] = 'Răspuns primit - Concert Aniversar UNBR'
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #d32f2f; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 30px; background-color: #ffebee; border-radius: 0 0 10px 10px; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📝 Răspuns Primit</h1>
                </div>
                <div class="content">
                    <p>Stimată/Stimat <strong>{guest_name}</strong>,</p>
                    
                    <p>Vă mulțumim pentru răspunsul dumneavoastră referitor la <strong>Concertul Aniversar UNBR din 24 noiembrie 2025</strong>.</p>
                    
                    <p>Ne pare rău că nu veți putea participa la acest eveniment special.</p>
                    
                    <p>Răspunsul dumneavoastră a fost înregistrat și vom actualiza lista participanților în consecință.</p>
                    
                    <p>Sperăm să avem ocazia să vă revedem la viitoarele evenimente UNBR!</p>
                    
                    <p>Cu stimă,<br><strong>Echipa Evenimente UNBR</strong></p>
                </div>
                <div class="footer">
                    <p>Universitatea Națională de Apărare "Carol I"</p>
                    <p>📧 evenimente@unbr.ro | 📞 +40213134875</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    message.attach(MIMEText(html_content, 'html', 'utf-8'))
    return message

def setup_concert_email_system() -> bool:
    """Configurează sistemul de emailuri pentru Concert 2025"""
    try:
        from smtp_utils import get_email_config
        config = get_email_config()
        
        if not config.email_password:
            print("❌ Nu pot configura sistemul fără parolă")
            return False
        
        print("🔧 Configurez sistemul de emailuri pentru Concert 2025...")
        
        # Creează folderele pentru concert
        if create_concert_folder(config):
            print("✅ Sistemul de organizare a fost configurat cu succes!")
            print("📁 Foldere create:")
            print(f"   • '{config.concert_folder_name}' - pentru invitații trimise")
            print(f"   • '{config.confirmations_folder_name}' - pentru confirmări/declinări")
            print("📧 Emailurile NU se vor mai salva în folderul Sent")
            return True
        else:
            print("❌ Eroare la configurarea sistemului")
            return False
            
    except Exception as e:
        print(f"❌ Eroare la configurarea sistemului: {e}")
        return False