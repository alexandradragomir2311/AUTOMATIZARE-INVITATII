"""
CONFIRM SERVER - ASYNC EMAIL + GOOGLE SHEETS
Trimite email în background, răspunde INSTANT, update Google Sheet
"""

from flask import Flask, request, render_template_string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import threading
import sys

# Import sheets_utils pentru Google Sheets
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sheets_utils import get_credentials
import gspread
from email_organization import save_sent_email_to_folder
from smtp_utils import get_email_config

app = Flask(__name__)

# SMTP evenimente@unbr.ro - PORT 587 cu STARTTLS
SMTP_SERVER = os.getenv('SMTP_SERVER', 'mail.unbr.ro')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS', 'evenimente@unbr.ro')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
SPREADSHEET_ID = '1-oAA8uUeDehcU-ckAHydsx8KujbXCWpZ0mMJIqWFoMg'
SHEET_NAME = 'INVITATII SI CONFIRMARI'

def update_sheet_background(token, response, persons=None):
    """Update Google Sheet în background"""
    def update():
        try:
            print(f"📊 Update Sheet: token={token[:15]}... resp={response} pers={persons}", flush=True)
            creds = get_credentials()
            client = gspread.authorize(creds)
            spreadsheet = client.open_by_key(SPREADSHEET_ID)
            sheet = spreadsheet.worksheet(SHEET_NAME)
            all_data = sheet.get_all_values()
            print(f"📊 Loaded {len(all_data)} rows from sheet", flush=True)
            
            # Găsește row după token
            for i, row in enumerate(all_data[1:], start=2):
                if len(row) > 9 and row[9] == token:
                    print(f"📊 Found token in row {i}", flush=True)
                    if response == 'da':
                        sheet.update_cell(i, 8, f"✔ Da - {persons}")
                        sheet.update_cell(i, 9, persons)
                        print(f"✅ Sheet updated: Da - {persons} persoane", flush=True)
                        
                        # ⭐ LOGIC NOUĂ: Dacă 2 persoane, adaugă linie nouă
                        print(f"🔍 Checking persons: '{persons}' (type: {type(persons).__name__})", flush=True)
                        if str(persons) == '2':
                            print(f"👥 Confirmare 2 persoane - adaug linie nouă...", flush=True)
                            
                            # Actualizează row-ul curent ca "Persoana 1/2"
                            sheet.update_cell(i, 8, "✔ Da - Persoana 1/2")
                            print(f"✅ Row {i} actualizat: Persoana 1/2", flush=True)
                            
                            # Verifică dacă următorul row există deja (Persoana 2/2)
                            has_person2 = False
                            if i < len(all_data):
                                next_row = all_data[i] if i < len(all_data) else None
                                if next_row and len(next_row) > 7 and "Persoana 2/2" in str(next_row[7]):
                                    has_person2 = True
                                    print(f"⚠️ Persoana 2/2 deja există în row {i+1}", flush=True)
                            
                            if not has_person2:
                                # Inserează row NOU după cel curent
                                sheet.insert_row([''] * 10, i + 1)
                                print(f"✅ Row nou inserat la poziția {i+1}", flush=True)
                                
                                # Copiază datele din row-ul original (coloanele A-G)
                                for col_idx in range(1, 8):  # Coloanele 1-7 (A-G)
                                    val = sheet.cell(i, col_idx).value
                                    sheet.update_cell(i + 1, col_idx, val)
                                
                                # Setează pentru Persoana 2/2 - ACELAȘI TOKEN!
                                sheet.update_cell(i + 1, 8, "✔ Da - Persoana 2/2")
                                sheet.update_cell(i + 1, 9, "Persoana 2")
                                sheet.update_cell(i + 1, 10, token)  # Același token!
                                print(f"✅ Linie nouă completată pentru Persoana 2/2", flush=True)
                    else:
                        sheet.update_cell(i, 8, '❌ Nu')
                        sheet.update_cell(i, 9, '-')
                        print(f"✅ Sheet updated: Nu particip", flush=True)
                    return
            print(f"⚠️ Token not found in Sheet", flush=True)
        except Exception as e:
            print(f"❌ Sheet error: {e}", flush=True)
            import traceback
            traceback.print_exc()
    
    # Start în background thread
    print(f"🔄 Launching Sheet update thread...", flush=True)
    thread = threading.Thread(target=update, daemon=True)
    thread.start()
    print(f"🔄 Sheet thread started", flush=True)

def get_email_from_sheet(token):
    """Găsește emailul din Sheet după token"""
    try:
        creds = get_credentials()
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        sheet = spreadsheet.worksheet(SHEET_NAME)
        all_data = sheet.get_all_values()
        
        for row in all_data[1:]:
            if len(row) > 9 and row[9] == token:
                return row[4] if len(row) > 4 else 'alexandradragomir23@yahoo.com'
        return 'alexandradragomir23@yahoo.com'
    except:
        return 'alexandradragomir23@yahoo.com'

def get_name_from_sheet(token):
    """Găsește numele complet din Sheet după token"""
    try:
        creds = get_credentials()
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        sheet = spreadsheet.worksheet(SHEET_NAME)
        all_data = sheet.get_all_values()
        
        for row in all_data[1:]:
            if len(row) > 9 and row[9] == token:
                nume = row[0] if len(row) > 0 else ''
                prenume = row[1] if len(row) > 1 else ''
                return f"{nume} {prenume}".strip()
        return 'Invitat'
    except:
        return 'Invitat'

def send_notification_to_admin(guest_name, guest_email, persons, response_type):
    """Trimite notificare către evenimente@unbr.ro când cineva confirmă"""
    def send():
        try:
            print(f"📧 Preparing admin notification...", flush=True)
            
            # Construiește mesajul
            if response_type == 'confirmare':
                subject = f"✅ CONFIRMARE: {guest_name} - {persons} {'persoană' if persons == '1' else 'persoane'}"
                html_body = f"""
                <html><body style="font-family: Arial; padding: 20px;">
                <h2 style="color: #4CAF50;">✅ Confirmare Primită</h2>
                <p><strong>Nume:</strong> {guest_name}</p>
                <p><strong>Email:</strong> {guest_email}</p>
                <p><strong>Număr persoane:</strong> {persons}</p>
                <p><strong>Data confirmării:</strong> {__import__('datetime').datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
                <hr>
                <p style="color: #666; font-size: 12px;">Verificați Google Sheet pentru detalii complete.</p>
                </body></html>
                """
            else:
                subject = f"❌ DECLINARE: {guest_name}"
                html_body = f"""
                <html><body style="font-family: Arial; padding: 20px;">
                <h2 style="color: #f44336;">❌ Nu Participă</h2>
                <p><strong>Nume:</strong> {guest_name}</p>
                <p><strong>Email:</strong> {guest_email}</p>
                <p><strong>Data răspunsului:</strong> {__import__('datetime').datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
                <hr>
                <p style="color: #666; font-size: 12px;">Verificați Google Sheet pentru detalii complete.</p>
                </body></html>
                """
            
            msg = MIMEMultipart('alternative')
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = EMAIL_ADDRESS  # Trimite către tine însuți!
            msg['Subject'] = subject
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            # Trimite prin SMTP
            print(f"📧 Connecting to SMTP {SMTP_SERVER}:{SMTP_PORT}...", flush=True)
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
                print(f"📧 Connected! Starting TLS={SMTP_USE_TLS}...", flush=True)
                if SMTP_USE_TLS:
                    server.starttls()
                    print(f"📧 TLS started, logging in...", flush=True)
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                print(f"📧 Logged in, sending admin notification...", flush=True)
                server.send_message(msg)
            print(f"✅ Notificare trimisă către {EMAIL_ADDRESS}", flush=True)
            
            # Salvează în folderul "Confirmări Concert 2025"
            try:
                config = get_email_config()
                if config:
                    folder_type = "confirmare" if response_type == "confirmare" else "declinare"
                    save_sent_email_to_folder(msg, config, folder_type)
                    print(f"📁 Email salvat în folderul 'Confirmări Concert 2025'", flush=True)
            except Exception as folder_error:
                print(f"⚠️ Nu s-a putut salva în folder: {folder_error}", flush=True)
        except Exception as e:
            print(f"❌ Admin notification error: {e}", flush=True)
            import traceback
            traceback.print_exc()
    
    # Start în background thread
    print(f"🔄 Launching admin notification thread...", flush=True)
    thread = threading.Thread(target=send, daemon=True)
    thread.start()
    print(f"🔄 Admin notification thread started", flush=True)

def send_email_background(to_email, subject, html_body):
    """Trimite email în thread separat - evenimente@unbr.ro SMTP"""
    def send():
        try:
            print(f"📧 Preparing email to {to_email}...", flush=True)
            msg = MIMEMultipart('alternative')
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            # SMTP standard cu STARTTLS
            print(f"📧 Connecting to SMTP {SMTP_SERVER}:{SMTP_PORT}...", flush=True)
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
                print(f"📧 Connected! Starting TLS={SMTP_USE_TLS}...", flush=True)
                if SMTP_USE_TLS:
                    server.starttls()
                    print(f"📧 TLS started, logging in...", flush=True)
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                print(f"📧 Logged in, sending...", flush=True)
                server.send_message(msg)
            print(f"✅ Email trimis: {to_email}", flush=True)
        except Exception as e:
            print(f"❌ Email error: {e}", flush=True)
            import traceback
            traceback.print_exc()
    
    # Start în background thread
    print(f"🔄 Launching email send thread...", flush=True)
    thread = threading.Thread(target=send, daemon=True)
    thread.start()
    print(f"🔄 Email thread started", flush=True)

@app.route('/')
def home():
    return "OK"

@app.route('/health')
def health():
    return {"status": "ok"}, 200

@app.route('/confirm', methods=['GET'])
def confirm():
    token = request.args.get('token', '')
    resp = request.args.get('resp', '')
    persoane = request.args.get('persoane', '1')
    
    if not token:
        return "Error", 400
    
    if not resp:
        return render_template_string("""
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Confirmare</title>
<style>
body { font-family: Arial; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; margin: 0; display: flex; align-items: center; justify-content: center; }
.box { background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); max-width: 400px; }
h1 { color: #333; margin: 0 0 20px 0; }
h2 { color: #666; font-weight: normal; margin: 0 0 30px 0; }
a { display: block; padding: 15px; margin: 10px 0; background: #4CAF50; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; cursor: pointer; }
a:hover { opacity: 0.9; }
.no { background: #f44336; }
</style>
</head><body>
<div class="box">
<h1>🎵 Concert UNBR</h1>
<h2>24 noiembrie 2025</h2>
<a href="/confirm?token={{ token }}&resp=da&persoane=1">✔ Particip - 1</a>
<a href="/confirm?token={{ token }}&resp=da&persoane=2">✔ Particip - 2</a>
<a href="/confirm?token={{ token }}&resp=nu" class="no">✖ Nu particip</a>
</div></body></html>
        """, token=token)
    
    if resp == 'da':
        print(f"🎯 CONFIRMARE DA - persoane={persoane}, token={token[:15]}...", flush=True)
        
        # UPDATE GOOGLE SHEET ÎN BACKGROUND
        print(f"📊 Starting Sheet update thread...", flush=True)
        update_sheet_background(token, 'da', persoane)
        
        # GĂSEȘTE DATELE INVITATULUI DIN SHEET
        print(f"📧 Getting guest info from sheet...", flush=True)
        guest_email = get_email_from_sheet(token)
        guest_name = get_name_from_sheet(token)
        print(f"📧 Found: {guest_name} ({guest_email})", flush=True)
        
        # TRIMITE NOTIFICARE CĂTRE evenimente@unbr.ro (DUBLĂ VERIFICARE)
        print(f"📧 Sending notification to evenimente@unbr.ro...", flush=True)
        send_notification_to_admin(
            guest_name,
            guest_email,
            persoane,
            'confirmare'
        )
        
        # RĂSPUNDE IMEDIAT
        return render_template_string("""
<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
body { font-family: Arial; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; margin: 0; display: flex; align-items: center; justify-content: center; }
.box { background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); max-width: 400px; }
h1 { color: #4CAF50; margin: 0; }
.emoji { font-size: 64px; margin-bottom: 20px; }
p { color: #666; }
</style>
</head><body>
<div class="box">
<div class="emoji">✅</div>
<h1>Confirmare primită!</h1>
<p>Am înregistrat participarea pentru {{ persoane }} persoane.</p>
<p style="margin-top: 20px; font-size: 14px; color: #999;">Email de confirmare vine în curând...</p>
</div></body></html>
        """, persoane=persoane)
    
    else:
        # UPDATE GOOGLE SHEET ÎN BACKGROUND
        update_sheet_background(token, 'nu', None)
        
        # GĂSEȘTE DATELE INVITATULUI DIN SHEET
        guest_email = get_email_from_sheet(token)
        guest_name = get_name_from_sheet(token)
        
        # TRIMITE NOTIFICARE CĂTRE evenimente@unbr.ro
        send_notification_to_admin(
            guest_name,
            guest_email,
            '0',
            'declinare'
        )
        
        # RĂSPUNDE IMEDIAT
        return render_template_string("""
<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
body { font-family: Arial; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; margin: 0; display: flex; align-items: center; justify-content: center; }
.box { background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); max-width: 400px; }
h1 { color: #333; }
p { color: #666; }
</style>
</head><body>
<div class="box">
<h1>Răspuns înregistrat</h1>
<p>Vă mulțumim pentru răspuns!</p>
</div></body></html>
        """)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
